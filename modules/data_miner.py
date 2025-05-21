import pandas as pd
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LinearRegression
from sklearn.metrics import accuracy_score, mean_squared_error

def perform_kmeans_clustering(df, n_clusters, columns):
    """Realiza clustering K-Means."""
    if isinstance(df, pd.DataFrame) and len(columns) >= 2:
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        df['cluster'] = kmeans.fit_predict(df[columns])
        return df
    return df

def perform_decision_tree_classification(df, features, target, test_size=0.2, random_state=42):
    """Realiza clasificación con árbol de decisión."""
    if isinstance(df, pd.DataFrame) and all(col in df.columns for col in features + [target]):
        X = df[features]
        y = df[target]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)
        model = DecisionTreeClassifier(random_state=random_state)
        model.fit(X_train, y_train)
        predictions = model.predict(X_test)
        accuracy = accuracy_score(y_test, predictions)
        return df, predictions, accuracy
    return df, None, None

def perform_linear_regression(df, features, target, test_size=0.2, random_state=42):
    """Realiza regresión lineal."""
    if isinstance(df, pd.DataFrame) and all(col in df.columns for col in features + [target]):
        X = df[features]
        y = df[target]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)
        model = LinearRegression()
        model.fit(X_train, y_train)
        predictions = model.predict(X_test)
        mse = mean_squared_error(y_test, predictions)
        return df, predictions, mse
    return df, None, None