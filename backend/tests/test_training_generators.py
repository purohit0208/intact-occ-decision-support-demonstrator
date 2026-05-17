from app.core.config import get_settings
from app.training.generate_bottleneck_data import generate_bottleneck_dataset
from app.training.generate_inventory_data import generate_inventory_dataset


def test_inventory_generator_has_nontrivial_class_coverage():
    frame = generate_inventory_dataset(samples=5000, seed=get_settings().random_seed + 3)
    proportions = frame["risk_level"].value_counts(normalize=True).to_dict()

    assert set(proportions) == {"LOW", "ELEVATED", "HIGH"}
    assert proportions["LOW"] >= 0.12
    assert proportions["ELEVATED"] >= 0.2
    assert proportions["HIGH"] <= 0.65


def test_bottleneck_generator_has_all_classes_represented():
    frame = generate_bottleneck_dataset(samples=5000, seed=get_settings().random_seed + 5)
    proportions = frame["dominant_bottleneck"].value_counts(normalize=True).to_dict()

    assert set(proportions) == {"Maintenance", "Catering", "Cleaning", "Boarding", "Refueling"}
    assert min(proportions.values()) >= 0.08
