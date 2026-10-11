"""XGBoost regressor definition for secure key rate prediction."""

from xgboost import XGBRegressor

from src.config import RANDOM_STATE


def get_model() -> XGBRegressor:
    """Return a configured XGBRegressor instance."""
    # return XGBRegressor(
    #     n_estimators=500,
    #     max_depth=8,
    #     learning_rate=0.05,
    #     subsample=0.8,
    #     colsample_bytree=0.8,
    #     min_child_weight=3,
    #     reg_alpha=0.1,
    #     reg_lambda=1.0,
    #     random_state=RANDOM_STATE,
    #     n_jobs=-1,
    # )
    return XGBRegressor(
        n_estimators=600,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        min_child_weight=3,
        reg_alpha=0.1,
        reg_lambda=1.0,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )
