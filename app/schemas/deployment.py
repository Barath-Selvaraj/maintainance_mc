from pydantic import BaseModel


class FeatureSelection(BaseModel):
    features: list[str]