import pandas as pd, itertools, sys, numpy as np, time, os, pathlib, warnings, matplotlib.pyplot as plt
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None) 
warnings.filterwarnings('ignore', category=pd.errors.SettingWithCopyWarning)


Haupttabelle            = pd.read_pickle('Irland_2002.pkl')
#Haupttabelle            = pd.read_pickle('cses_imd.pkl')

os.makedirs               ('Zwischenablage', exist_ok=True)
Liste_Country_namen     = sorted(list(set(list(Haupttabelle['Country']))))

a1_list, b1_list        = zip(*[[a, b] for a in range(1, 10) for b in range(1, 10) if  a != b])
Präferenzkombinationen  = pd.DataFrame({'A1': a1_list,'B1': b1_list})
Ranking_Variablen       = ['A','B','C','D','E','F','G','H','I']
Präferenz_Variablen     = ['SA','SB','SC','SD','SE','SF','SG','SH','SI']
Kombiliste              = [letter1 + letter2 for letter1 in Ranking_Variablen for letter2 in Ranking_Variablen if letter1 != letter2]

for column_name in Kombiliste: Präferenzkombinationen[column_name] = 0
Pk_ah = Präferenzkombinationen.copy()
Pk_ds = Präferenzkombinationen.copy()

for Country_Year_name in Liste_Country_namen:
    Teil_Haupttabelle     = Haupttabelle[Haupttabelle['Country'] == Country_Year_name]
    Ranking_Teiltabelle   = Teil_Haupttabelle[['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']]
    Präferenz_Teiltabelle = Teil_Haupttabelle[['SA','SB','SC','SD','SE','SF','SG','SH','SI']]
    Time = time.time()
    for (index_R, row_R), (index_P, row_P) in zip(Ranking_Teiltabelle.iterrows(), Präferenz_Teiltabelle.iterrows()):
        for index_a1, a1 in enumerate(row_R):
            for index_b1, b1 in enumerate(row_R):
                if a1 != b1 and a1 < 10 and b1 < 10:
                    Spalte    = Ranking_Variablen[index_a1] + Ranking_Variablen[index_b1]
                    row_P     = list(row_P)
                    Präf_diff = row_P[index_a1] - row_P[index_b1]
                    Zeile     = (Pk_ah['A1'] == a1) & (Pk_ah['B1'] == b1)
                    
                    if Spalte in Pk_ah.columns:
                        Pk_ah.loc[Zeile, Spalte] += 1
                        Pk_ds.loc[Zeile, Spalte] += Präf_diff

    Pk_ah = Pk_ah[(Pk_ah.iloc[:, 2:] != 0).any(axis=1)]
    Pk_ds = Pk_ds[(Pk_ds.iloc[:, 2:] != 0).any(axis=1)]
   

    for Kombination in Kombiliste:
        Pk_ah_kombination   = Pk_ah[Pk_ah[Kombination] != 0][['A1','B1',Kombination]]
        Pk_ds_kombination   = Pk_ds[Pk_ds[Kombination] != 0][['A1','B1',Kombination]]
        if Pk_ds_kombination.empty: continue

        Average_differenz   = np.sum(Pk_ds_kombination[Kombination]) / np.sum(Pk_ah_kombination[Kombination])

        Pk_ds_kombination                                         = Pk_ds_kombination.rename(columns={Kombination: 'Abs Skala Diff'})
        Pk_ds_kombination['Avg Country Year Kombi']            = Average_differenz
        #Pk_ds_kombination['Unterschied zum Durchschnitt Absolut'] = round(Pk_ds_kombination['Absolute Skala Differenz'] - Average_differenz, 2)
        Pk_ds_kombination['Kombination'] = Kombination
        Pk_ds_kombination['Country Year'] = Country_Year_name


        Pk_ds_kombination.to_pickle(f'Zwischenablage/Teilauswertung_{Country_Year_name}_{Kombination}.pkl')
    print([Country_Year_name,time.time()-Time])

directory   = pathlib.Path('Zwischenablage')
dfs         = []
for file_path in directory.glob('*.pkl'): dfs.append(pd.read_pickle(file_path))
Gesamtauswertung   = pd.concat(dfs, ignore_index=True)
Gesamtauswertung    .to_pickle('Gesamtauswertung.pkl')
print(f"Concatenated DataFrame shape: {Gesamtauswertung.shape}")
#print(Gesamtauswertung)


print('fertig!')


Gesamtauswertung = Gesamtauswertung.groupby('Kombination').first()

#print(Gesamtauswertung.index)
#sys.exit()

x_values = range(len(Gesamtauswertung['Avg Country Year Kombi']))
plt.scatter(x_values, Gesamtauswertung['Avg Country Year Kombi'], color='blue', label='Punkte')
for i, label in enumerate(Gesamtauswertung.index):
    plt.text(x_values[i], Gesamtauswertung['Avg Country Year Kombi'].iloc[i], label, fontsize=8, ha='right', va='bottom')

plt.xlabel('Index')
plt.ylabel('Punkte')
plt.title('Avg Country Year Kombi Punkte')
plt.legend()
plt.savefig('Absolute Skala Differenz.png')
plt.show()
