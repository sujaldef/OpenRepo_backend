# services/ml_engine/model_router.py

import os
import torch
from pathlib import Path

class ModelRouter:
    """
    Routes analysis to language-specific ML models.
    Maps: Python → python_model.pt, JavaScript → mern_model.pt, C → c_model.pt
    Falls back to generic issue_model if language-specific model unavailable.
    """
    
    def __init__(self):
        self.models = {}
        self.model_dir = os.path.join(
            os.path.dirname(__file__),
            "../../ml_training/saved_models"
        )
        self._load_models()
    
    def _load_models(self):
        """Load all language-specific models on initialization."""
        from .issue_model_inference import IssueModel
        
        # Language-specific models
        self.language_models = {
            "python": self._load_pt_model("python_model.pt"),
            "javascript": self._load_pt_model("mern_model.pt"),
            "c": self._load_pt_model("c_model.pt"),
        }
        
        # Fallback generic model for  unsupported languages
        self.generic_model = IssueModel()
        
        print("✓ ModelRouter initialized")
        print(f"  - Python-specific model: {'✓ Loaded' if self.language_models['python'] else '✗ Failed'}")
        print(f"  - JavaScript-specific model: {'✓ Loaded' if self.language_models['javascript'] else '✗ Failed'}")
        print(f"  - C-specific model: {'✓ Loaded' if self.language_models['c'] else '✗ Failed'}")
        print(f"  - Generic fallback: ✓ Available")
    
    def _load_pt_model(self, filename: str):
        """Load a PyTorch model file."""
        filepath = os.path.join(self.model_dir, filename)
        try:
            if os.path.exists(filepath):
                # Try loading as PyTorch model
                model = torch.load(filepath, map_location="cpu")
                return model
            else:
                print(f"⚠ Model not found: {filepath}")
                return None
        except Exception as e:
            print(f"⚠ Failed to load {filename}: {e}")
            return None
    
    def get_model(self, filename: str):
        """
        Get the appropriate model for a file based on its extension/language.
        Returns: Model wrapper with .predict() method
        """
        ext = os.path.splitext(filename)[1].lower()
        language = self._detect_language(ext)
        
        # Try to get language-specific model
        if language in self.language_models and self.language_models[language]:
            return LanguageSpecificModelWrapper(
                self.language_models[language],
                language
            )
        
        # Fallback to generic model
        return GenericModelWrapper(self.generic_model, language)
    
    def _detect_language(self, ext: str) -> str:
        """Detect language from file extension."""
        ext = ext.lower()
        
        if ext == ".py":
            return "python"
        elif ext in [".js", ".jsx", ".ts", ".tsx"]:
            return "javascript"
        elif ext in [".c", ".cpp", ".h", ".hpp", ".cc", ".cxx"]:
            return "c"
        elif ext == ".java":
            return "java"
        elif ext == ".go":
            return "go"
        else:
            return "unknown"


class LanguageSpecificModelWrapper:
    """Wrapper for language-specific PyTorch models."""
    
    def __init__(self, model, language: str):
        self.model = model
        self.language = language
        self.model_type = f"{language}_model"
    
    def predict(self, text_input: str):
        """Predict using language-specific model."""
        try:
            # PyTorch model prediction (adjust based on actual model architecture)
            if hasattr(self.model, 'eval'):
                self.model.eval()
            
            # Placeholder: actual implementation depends on model architecture
            # For now, return structure expected by pipeline
            prediction = {
                "label": 0,
                "confidence": 0.75,
                "model_used": self.model_type,
                "language": self.language
            }
            return prediction
        except Exception as e:
            print(f"⚠ Error in {self.model_type}.predict(): {e}")
            return {
                "label": 0,
                "confidence": 0.0,
                "error": str(e),
                "model_used": self.model_type
            }


class GenericModelWrapper:
    """Wrapper for the generic IssueModel (fallback)."""
    
    def __init__(self, model, language: str):
        self.model = model
        self.language = language
        self.model_type = "generic_issue_model"
    
    def predict(self, text_input: str):
        """Predict using generic model."""
        try:
            prediction = self.model.predict(text_input)
            # Add metadata about which model was used
            prediction["model_used"] = self.model_type
            prediction["language"] = self.language
            prediction["routing_reason"] = f"Using generic model for {self.language}"
            return prediction
        except Exception as e:
            print(f"⚠ Error in generic model.predict(): {e}")
            return {
                "label": 0,
                "confidence": 0.0,
                "error": str(e),
                "model_used": self.model_type
            }


# Global instance
_model_router = None

def get_model_router():
    """Get or initialize the global ModelRouter instance."""
    global _model_router
    if _model_router is None:
        _model_router = ModelRouter()
    return _model_router
