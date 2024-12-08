import pandas as pd

def load_data(filepath):
    try:
        df = pd.read_csv(filepath, sep = ';')
    except FileNotFoundError as e:
        print("Error: File not found.")
        exit()

    #print(df.head(10).to_markdown(tablefmt="grid"))
    return df

def searchByName(df, name):
    return df[df.NameOfMedicine == name].to_markdown()

def searchByIngredient(df, name):
    return df[df.ActiveSubstance == name].to_markdown()

medsDf = load_data('../resources/medicines.csv')

print(searchByName(medsDf, 'Wyost'))
print(searchByIngredient(medsDf, 'Ibuprofen'))
#print(medsDf.info())
