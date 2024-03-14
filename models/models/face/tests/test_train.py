from face.train import get_individual_sets
import pytest


@pytest.mark.parametrize(
    "samples, indices, individual_sets",
    [
        (
            [
                ("1_cs_joy_1.0_c.png", 1),
                ("2_cs_anger_1.0_c.png", 2),
                ("3_cs_fear_1.0_c.png", 3),
                ("1_mf_joy_1.0_c.png", 1),
                ("2_mf_anger_1.0_c.png", 2),
                ("3_mf_fear_1.0_c.png", 3),
                ("1_km_joy_1.0_c.png", 1),
                ("2_km_anger_1.0_c.png", 2),
                ("3_km_fear_1.0_c.png", 3),
            ],
            [0, 1, 2, 3, 4, 5, 6, 7, 8],
            {
                "cs": [0, 1, 2],
                "mf": [3, 4, 5],
                "km": [6, 7, 8],
            },
        ),
        (
            [
                ("1_cs_joy_1.0_c.png", 1),
                ("1_mf_joy_1.0_c.png", 1),
                ("1_km_joy_1.0_c.png", 1),
                ("2_mf_anger_1.0_c.png", 2),
                ("2_cs_anger_1.0_c.png", 2),
                ("2_km_anger_1.0_c.png", 2),
                ("3_cs_fear_1.0_c.png", 3),
                ("3_mf_fear_1.0_c.png", 3),
                ("3_km_fear_1.0_c.png", 3),
                ("3_km_fear_1.1_c.png", 3),
                ("3_km_fear_1.2_c.png", 3),
            ],
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            {
                "cs": [0, 4, 6],
                "mf": [1, 3, 7],
                "km": [2, 5, 8, 9, 10],
            },
        ),
        (
            [
                ("1_cs_joy_1.0_c.png", 1),
                ("1_mf_joy_1.0_c.png", 1),
                ("1_km_joy_1.0_c.png", 1),
            ],
            [0],
            {
                "cs": [0],
            },
        ),
    ],
)
def test_individual_sets(samples, indices, individual_sets):
    assert get_individual_sets(samples, indices) == individual_sets
