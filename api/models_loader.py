import joblib
from ultralytics import YOLO

class ModelLoader:
    def __init__(self):
        self.yolo_model = YOLO('ml_models/best.pt')
        self.rf_model = joblib.load('ml_models/random_forest_model.joblib')
        self.label_encoder = joblib.load('ml_models/label_encoder.joblib')
        self.training_columns = joblib.load('ml_models/rf_feature_columns.joblib')
        self.all_labels = self.label_encoder.classes_
        self.master_point_list = self._criar_mapeamento_pontos()

    def _criar_mapeamento_pontos(self):
        return {
            'md': [l for l in self.all_labels if 'direito' not in l and 'esquerdo' not in l],
            'me': [l for l in self.all_labels if 'direito' not in l and 'esquerdo' not in l],
            'pd': [l for l in self.all_labels if l.endswith('_direito')],
            'pe': [l for l in self.all_labels if l.endswith('_esquerdo')]
        }

# Instância global para importar nos serviços
model_loader = ModelLoader()