import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor
from sklearn.svm import SVR
import xgboost as xgb
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from src import config as C

# Fixed seeds for reproducibility
np.random.seed(C.SEED)
torch.manual_seed(C.SEED)

class PersistenceModel:
    """Baseline 1: Persistence (WL(t+h) = WL(t))."""
    def fit(self, X, y):
        pass
    def predict(self, X_df):
        # Predict Delta WL = 0
        return np.zeros(len(X_df))

class PersistenceTrendModel:
    """Baseline 2: Persistence + Trend."""
    def fit(self, X, y):
        pass
    def predict(self, X_df, horizon):
        # Trend: WL(t) - WL(t-1)
        if 'Delta_1d' in X_df.columns:
            trend = X_df['Delta_1d'].values
        else:
            trend = X_df['WL_lag_0'].values - X_df['WL_lag_1'].values
        return horizon * trend

class AnomalyPersistenceModel:
    """Baseline 3: Anomaly Persistence."""
    def __init__(self, doy_mean_dict):
        self.doy_mean_dict = doy_mean_dict
        
    def fit(self, X, y):
        pass
        
    def predict(self, df_rows, horizon):
        # Target day of year
        target_doy = (df_rows['Date'] + pd.Timedelta(days=horizon)).dt.dayofyear
        curr_doy = df_rows['DayOfYear'].values
        
        target_climatology = np.array([self.doy_mean_dict.get(d, 15.5) for d in target_doy])
        curr_climatology = np.array([self.doy_mean_dict.get(d, 15.5) for d in curr_doy])
        
        wl_curr = df_rows['WL'].values
        anomaly_curr = wl_curr - curr_climatology
        
        predicted_wl = target_climatology + anomaly_curr
        predicted_delta = predicted_wl - wl_curr
        return predicted_delta

class PyTorchLSTM(nn.Module):
    def __init__(self, input_dim, hidden_dim=32, num_layers=1):
        super(PyTorchLSTM, self).__init__()
        self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_dim, 1)
        
    def forward(self, x):
        out, _ = self.lstm(x)
        out = self.fc(out[:, -1, :])
        return out.squeeze(-1)

class LSTMForecaster:
    """LSTM model predicting Delta WL."""
    def __init__(self, hidden_dim=32, epochs=40, lr=0.01, batch_size=64):
        self.hidden_dim = hidden_dim
        self.epochs = epochs
        self.lr = lr
        self.batch_size = batch_size
        self.scaler_X = StandardScaler()
        self.scaler_y = StandardScaler()
        self.model = None
        
    def fit(self, X_train, y_train):
        X_scaled = self.scaler_X.fit_transform(X_train)
        y_scaled = self.scaler_y.fit_transform(y_train.reshape(-1, 1)).flatten()
        
        # Reshape X to 3D tensor: (samples, timesteps=1, features)
        X_tensor = torch.tensor(X_scaled, dtype=torch.float32).unsqueeze(1)
        y_tensor = torch.tensor(y_scaled, dtype=torch.float32)
        
        dataset = TensorDataset(X_tensor, y_tensor)
        loader = DataLoader(dataset, batch_size=self.batch_size, shuffle=True)
        
        self.model = PyTorchLSTM(input_dim=X_train.shape[1], hidden_dim=self.hidden_dim)
        criterion = nn.MSELoss()
        optimizer = optim.Adam(self.model.parameters(), lr=self.lr)
        
        self.model.train()
        for epoch in range(self.epochs):
            for bx, by in loader:
                optimizer.zero_grad()
                out = self.model(bx)
                loss = criterion(out, by)
                loss.backward()
                optimizer.step()
                
    def predict(self, X_test):
        self.model.eval()
        X_scaled = self.scaler_X.transform(X_test)
        X_tensor = torch.tensor(X_scaled, dtype=torch.float32).unsqueeze(1)
        with torch.no_grad():
            preds_scaled = self.model(X_tensor).numpy()
        preds = self.scaler_y.inverse_transform(preds_scaled.reshape(-1, 1)).flatten()
        return preds

def get_model_pipeline(model_name, **params):
    """Factory function returning model object."""
    if model_name == 'LinearRegression':
        return LinearRegression()
    elif model_name == 'Ridge':
        alpha = params.get('alpha', 1.0)
        return Ridge(alpha=alpha, random_state=C.SEED)
    elif model_name == 'Lasso':
        alpha = params.get('alpha', 0.01)
        return Lasso(alpha=alpha, random_state=C.SEED)
    elif model_name == 'RandomForest':
        n_estimators = params.get('n_estimators', 100)
        max_depth = params.get('max_depth', 10)
        return RandomForestRegressor(n_estimators=n_estimators, max_depth=max_depth, random_state=C.SEED, n_jobs=-1)
    elif model_name == 'XGBoost':
        n_estimators = params.get('n_estimators', 100)
        max_depth = params.get('max_depth', 5)
        learning_rate = params.get('learning_rate', 0.05)
        return xgb.XGBRegressor(n_estimators=n_estimators, max_depth=max_depth, learning_rate=learning_rate, random_state=C.SEED, n_jobs=-1)
    elif model_name == 'SVR':
        C_val = params.get('C', 1.0)
        epsilon = params.get('epsilon', 0.1)
        return SVR(C=C_val, epsilon=epsilon)
    elif model_name == 'LSTM':
        return LSTMForecaster(hidden_dim=params.get('hidden_dim', 32), epochs=params.get('epochs', 40))
    else:
        raise ValueError(f"Unknown model name: {model_name}")
