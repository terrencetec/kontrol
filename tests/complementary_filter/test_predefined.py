"""Tests for kontrol.complementary_filter.predefined"""
import numpy as np

import kontrol.complementary_filter.predefined


def test_predefined():
    """Tests for various predefined filters."""
    ## Simply calling them to test for errors.
    coefs = np.random.random(4)
    kontrol.complementary_filter.predefined.sekiguchi(coefs)
    kontrol.complementary_filter.predefined.modified_sekiguchi(coefs)
    coefs = np.random.random(7)
    kontrol.complementary_filter.predefined.lucia(coefs)
