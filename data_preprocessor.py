import pandas as pd
import os
import numpy as np

class DataPreprocessor:
    def __init__(self, dataset_path=None):
        if dataset_path is None:
            # Get the absolute path to the dataset
            current_dir = os.path.dirname(os.path.abspath(__file__))
            dataset_path = os.path.join(current_dir, 'dataset.csv')
        
        self.dataset_path = dataset_path
        self.data = None
        self.normalized_data = None

    @staticmethod
    def list_available_datasets(data_dir=None):
        """List CSV datasets from the project data directory."""
        if data_dir is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            data_dir = current_dir

        if not os.path.exists(data_dir):
            return []

        return sorted([
            filename for filename in os.listdir(data_dir)
            if filename.endswith('.csv')
        ])
        
    def load_data(self):
        """Load the CSV dataset"""
        try:
            self.data = pd.read_csv(self.dataset_path)
            print(f"✓ Dataset loaded: {len(self.data)} rows")
            return self.data
        except FileNotFoundError:
            print(f"✗ Dataset file not found at {self.dataset_path}")
            return None

    def _ensure_columns(self, df, required_columns):
        """Check if all required columns exist in the dataframe."""
        missing = [col for col in required_columns if col not in df.columns]
        return missing

    def _resolve_unit_costs(self, df):
        """Use tariff columns if provided, otherwise use fixed default costs."""
        if {'c_grid', 'c_water', 'c_gas'}.issubset(df.columns):
            return df['c_grid'], df['c_water'], df['c_gas']

        c_grid = pd.Series(8.5, index=df.index)
        c_water = pd.Series(2.5, index=df.index)
        c_gas = pd.Series(3.2, index=df.index)
        return c_grid, c_water, c_gas
    
    def preprocess(self):
        """Apply preprocessing: handle missing values, normalize, categorize"""
        if self.data is None:
            self.load_data()

        if self.data is None:
            return None
        
        df = self.data.copy()

        # Support alternate column naming used by country-specific datasets.
        column_aliases = {
            'temperature_c': 'temperature',
            'humidity_percent': 'humidity',
            'rainfall_mm': 'rainfall',
            'solar_irradiance_wm2': 'solar_irradiance',
            'electricity_consumption_kwh': 'electricity_consumption',
            'water_consumption_m3': 'water_consumption',
            'gas_consumption_m3': 'gas_consumption',
            'renewable_energy_kwh': 'renewable_energy_production',
            'electricity_cost_tk': 'electricity_cost',
            'water_cost_tk': 'water_cost',
            'gas_cost_tk': 'gas_cost',
            'hourly_cost_tk': 'hourly_cost',
            'daily_cost_tk': 'daily_cost'
        }
        rename_map = {
            old_col: new_col for old_col, new_col in column_aliases.items()
            if old_col in df.columns and new_col not in df.columns
        }
        if rename_map:
            df.rename(columns=rename_map, inplace=True)
        
        # Handle missing values
        df.fillna(0, inplace=True)

        # If this is algorithm benchmark data, no resource normalization is needed.
        if {'algorithm', 'objective_cost', 'execution_time_ms'}.issubset(df.columns):
            self.normalized_data = df
            print("✓ Data preprocessing complete")
            return self.normalized_data

        required_cols = [
            'temperature', 'rainfall', 'solar_irradiance',
            'electricity_consumption', 'water_consumption', 'gas_consumption',
            'renewable_energy_production'
        ]
        missing = self._ensure_columns(df, required_cols)
        if missing:
            print(f"✗ Missing required columns: {', '.join(missing)}")
            return None
        
        # Normalize resource consumption values (0-1 scale)
        consumption_cols = ['electricity_consumption', 'water_consumption', 'gas_consumption']
        for col in consumption_cols:
            max_val = df[col].max()
            if max_val > 0:
                df[f'{col}_normalized'] = df[col] / max_val
        
        # Normalize solar irradiance (0-1 scale)
        max_solar = df['solar_irradiance'].max()
        if max_solar > 0:
            df['solar_irradiance_normalized'] = df['solar_irradiance'] / max_solar
        
        # Normalize temperature (0-1 scale, 15-40°C range)
        df['temperature_normalized'] = (df['temperature'] - 15) / (40 - 15)
        df['temperature_normalized'] = df['temperature_normalized'].clip(0, 1)
        
        # Normalize humidity (0-1 scale, 0-100%) if available
        if 'humidity' in df.columns:
            df['humidity_normalized'] = df['humidity'] / 100
        
        # Weather categorization: Map to numeric values
        weather_mapping = {'Clear': 0, 'Cloudy': 1, 'Rainy': 2, 'Sunny': 0}
        if 'weather_condition' in df.columns:
            df['weather_category'] = df['weather_condition'].map(weather_mapping)
        
        # Calculate cost function per hour using taka-based pricing.
        # J = (C_grid * E_grid + C_water * W_muni + C_gas * G_cons)
        if 'hourly_cost' not in df.columns:
            c_grid, c_water, c_gas = self._resolve_unit_costs(df)

            df['hourly_cost'] = (
                c_grid * df['electricity_consumption'] +
                c_water * df['water_consumption'] +
                c_gas * df['gas_consumption']
            )
        
        # Calculate efficiency metric (renewable energy / total consumption)
        df['total_consumption'] = (
            df['electricity_consumption'] +
            df['water_consumption'] +
            df['gas_consumption']
        )
        
        df['efficiency'] = np.where(
            df['total_consumption'] > 0,
            df['renewable_energy_production'] / df['total_consumption'],
            0
        )
        
        self.normalized_data = df
        print("✓ Data preprocessing complete")
        return self.normalized_data
    
    def get_summary(self):
        """Get summary statistics of the dataset"""
        if self.normalized_data is None:
            self.preprocess()

        if self.normalized_data is None:
            return {}

        # Summary for algorithm benchmark datasets.
        if {'algorithm', 'objective_cost', 'execution_time_ms'}.issubset(self.normalized_data.columns):
            benchmark_summary = {
                'records': len(self.normalized_data),
                'algorithms': int(self.normalized_data['algorithm'].nunique()),
                'avg_objective_cost': round(self.normalized_data['objective_cost'].mean(), 2),
                'avg_execution_time_ms': round(self.normalized_data['execution_time_ms'].mean(), 2),
                'best_objective_cost': round(self.normalized_data['objective_cost'].min(), 2)
            }
            return benchmark_summary

        start_ts = self.normalized_data['timestamp'].iloc[0] if 'timestamp' in self.normalized_data.columns else 'N/A'
        end_ts = self.normalized_data['timestamp'].iloc[-1] if 'timestamp' in self.normalized_data.columns else 'N/A'
        
        summary = {
            'total_records': len(self.normalized_data),
            'period_start': start_ts,
            'period_end': end_ts,
            'avg_temperature': round(self.normalized_data['temperature'].mean(), 2),
            'max_temperature': round(self.normalized_data['temperature'].max(), 2),
            'min_temperature': round(self.normalized_data['temperature'].min(), 2),
            'total_rainfall': round(self.normalized_data['rainfall'].sum(), 2),
            'total_solar_irradiance': round(self.normalized_data['solar_irradiance'].sum(), 2),
            'total_electricity_consumption': round(self.normalized_data['electricity_consumption'].sum(), 2),
            'total_water_consumption': round(self.normalized_data['water_consumption'].sum(), 2),
            'total_gas_consumption': round(self.normalized_data['gas_consumption'].sum(), 2),
            'total_renewable_energy': round(self.normalized_data['renewable_energy_production'].sum(), 2),
            'total_cost': round(self.normalized_data['hourly_cost'].sum(), 2),
            'average_efficiency': round(self.normalized_data['efficiency'].mean(), 2)
        }

        # Keep backward compatibility with existing main.py output key.
        summary['total_daily_cost'] = summary['total_cost']
        return summary
    
    def get_hour_data(self, hour):
        """Get data for a specific hour (0-23)"""
        if self.normalized_data is None:
            self.preprocess()
        
        if 0 <= hour < len(self.normalized_data):
            return self.normalized_data.iloc[hour].to_dict()
        return None


# Example usage
if __name__ == "__main__":
    processor = DataPreprocessor()
    processor.load_data()
    processor.preprocess()
    
    print("\n📊 Dataset Summary:")
    summary = processor.get_summary()
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    print("\n📍 Sample Hour Data (Hour 12):")
    hour_12 = processor.get_hour_data(12)
    for key, value in hour_12.items():
        print(f"  {key}: {value}")
