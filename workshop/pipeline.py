import pandas as pd
from datasets import load_dataset

from sentence_transformers import SentenceTransformer

from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.metrics import classification_report
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression

from workshop.config import label_names

class Pipeline:
    def load_dataset(self):
        dataset =  load_dataset("PolyAI/banking77", revision="main") # taking the data from the main branch
    
        train_data = pd.DataFrame(dataset['train'])
        test_data = pd.DataFrame(dataset['test'])

        train_data["label_name"] = train_data["label"].apply(lambda x: label_names[x])
        test_data["label_name"] = test_data["label"].apply(lambda x: label_names[x])

        return train_data, test_data
    
    def create_embeddings(self, train_data):
        print("Encoding embeddings")
        self.embeddings_model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
        
        train_text_lists = train_data.text.tolist()

        train_embeddings = self.embeddings_model.encode(train_text_lists, show_progress_bar=True)

        return train_embeddings
    
    def train(self, train_data = None, test_data = None, train_embeddings = None):
        if not isinstance(train_data, pd.DataFrame) or not isinstance(test_data, pd.DataFrame):
            train_data, test_data = self.load_dataset()

        
        print("Training KNN")
        knn = KNeighborsClassifier(n_neighbors=5, weights='distance', metric='cosine')

        if not isinstance(train_embeddings, pd.DataFrame):
            train_embeddings = self.create_embeddings(train_data)

        X_train, X_val, y_train, y_val = train_test_split(
            train_embeddings, train_data['label_name'], test_size=0.2, random_state=0)

        knn.fit(X_train, y_train)
        y_pred = knn.predict(X_val)
        print(classification_report(y_val, y_pred))

        self.model = knn
        self.test_model("I still haven't recieved my card, when will it be ready?")

        return self.model
    

    def test_model(self, text_input):
        print(f"Prediction for {text_input}")
        print(self.model.predict(self.embeddings_model.encode(text_input).reshape(1, -1)))




if __name__ == "__main__":
    import fire
    fire.Fire(Pipeline)