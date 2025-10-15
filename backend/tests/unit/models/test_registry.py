"""Tests for models registry module."""

import pytest


class TestModelsRegistry:
    """Test models registry module."""
    
    def test_registry_import(self):
        """Test that registry module can be imported."""
        try:
            from app.models import registry
            assert registry is not None
        except ImportError as e:
            pytest.fail(f"Failed to import registry: {e}")
    
    def test_models_list_exists(self):
        """Test that MODELS list exists in registry."""
        from app.models import registry
        assert hasattr(registry, 'MODELS')
        assert isinstance(registry.MODELS, list)
    
    def test_models_list_not_empty(self):
        """Test that MODELS list contains models."""
        from app.models import registry
        assert len(registry.MODELS) > 0
    
    def test_user_model_in_registry(self):
        """Test that User model is in registry."""
        from app.models import registry
        from app.models.user import User
        assert User in registry.MODELS
    
    def test_role_model_in_registry(self):
        """Test that Role model is in registry."""
        from app.models import registry
        from app.models.role import Role
        assert Role in registry.MODELS
    
    def test_build_model_in_registry(self):
        """Test that Build model is in registry."""
        from app.models import registry
        from app.models.build import Build
        assert Build in registry.MODELS
    
    def test_composition_model_in_registry(self):
        """Test that Composition model is in registry."""
        from app.models import registry
        from app.models.composition import Composition
        assert Composition in registry.MODELS
    
    def test_association_tables_in_registry(self):
        """Test that association tables are in registry."""
        from app.models import registry
        from app.models.association_tables import build_profession, role_permissions
        assert build_profession in registry.MODELS
        assert role_permissions in registry.MODELS
    
    def test_all_exported_models(self):
        """Test that __all__ contains MODELS."""
        from app.models import registry
        assert "__all__" in dir(registry)
        assert "MODELS" in registry.__all__
