
# pipeline_lib.py

import pandas as pd

from textblob import TextBlob

def fix_spelling_errors(df):
    # Itera sobre cada columna de texto en el DataFrame
    for col in df.select_dtypes(include=['object']).columns:
        # Aplica la corrección ortográfica a cada celda de la columna
        df[col] = df[col].apply(lambda x: str(TextBlob(x).correct()) if isinstance(x, str) else x)
    return df


def handle_null_values(df):
    """
    Esta función maneja los valores nulos en el DataFrame.
    Se reemplazan los valores nulos con la mediana de cada columna numérica y con el valor más frecuente para las columnas categóricas.
    """
    # Reemplazar los valores nulos en columnas numéricas con la mediana
    for column in df.select_dtypes(include=['float64', 'int64']).columns:
        median_value = df[column].median()  # Calcular la mediana
        df[column].fillna(median_value, inplace=True)  # Reemplazar nulos con la mediana

    # Reemplazar los valores nulos en columnas categóricas con el valor más frecuente
    for column in df.select_dtypes(include=['object']).columns:
        mode_value = df[column].mode()[0]  # Calcular el valor más frecuente
        df[column].fillna(mode_value, inplace=True)  # Reemplazar nulos con el valor más frecuente

    return df


