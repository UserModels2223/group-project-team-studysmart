import pandas as pd
m = UIFeatures()
df = pd.read_csv(pool[u"vocabulary_marked.csv"])
for row in df.itertuples():
    m.add_fact(Fact(fact_id = row.id, context_1= row.context_1, context_2 =row.context_2, answer=row.answer, chosen_context=row.context_1, question=row.question))
