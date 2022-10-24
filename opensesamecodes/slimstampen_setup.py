import pandas as pd
m = UIFeatures()
df = pd.read_csv(pool[u"vocabulary_marked.csv"])
df = df.drop("id", axis =1) #remove id column to set automatically
if m.SHUFFLE_DATA_BEFORE_LOADING == True:
    df = df.sample(
        frac = 1,
        random_state=1).reset_index()

for i,row in enumerate(df.itertuples()):
    m.add_fact(Fact(fact_id = i, context_1= row.context_1, context_2 =row.context_2, answer=row.answer, chosen_context=row.context_1, question=row.question, encounter_2=False))

# for row in df.itertuples():
#     m.add_fact(Fact(fact_id = row.id, context_1= row.context_1, context_2 =row.context_2, answer=row.answer, chosen_context=row.context_1, question=row.question, encounter_2=False))

