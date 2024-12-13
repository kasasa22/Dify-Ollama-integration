import unittest
from core.model_runtime.model_providers.model_provider_factory import ModelProviderFactory
from core.model_runtime.entities.model_entities import ModelType

class TestMPlugOWLProvider(unittest.TestCase):
    def setUp(self):
        self.factory = ModelProviderFactory()

    def test_provider_exists(self):
        """Test if mPlugOWL provider is registered"""
        providers = self.factory.get_providers()
        provider_names = [provider.provider for provider in providers]
        self.assertIn('mplugowl', provider_names, "mPlugOWL provider not found in registered providers")

    def test_provider_models(self):
        """Test if we can get models from the provider"""
        models = self.factory.get_models(
            provider='mplugowl',
            model_type=ModelType.LLM
        )
        self.assertTrue(len(models) > 0, "No models found for mPlugOWL provider")

    def test_provider_instance(self):
        """Test if we can get provider instance"""
        try:
            provider = self.factory.get_provider_instance('mplugowl')
            self.assertIsNotNone(provider, "Could not get mPlugOWL provider instance")
        except Exception as e:
            self.fail(f"Failed to get provider instance: {str(e)}")

if __name__ == '__main__':
    unittest.main()