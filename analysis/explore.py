import pandas as pd

from app.records import load_records

df = pd.DataFrame(load_records())

# fact 1: how many records and how many different vaccine entries
print("Fact 1:", len(df), "records,", df["vaccine"].nunique(), "different vaccine entries")

# fact 2: the most common route (the first word of route_site)
routes = df["route_site"].str.split(",").str[0]
print("Fact 2: most common route is", routes.value_counts().idxmax(),
      "with", routes.value_counts().max(), "records")

# fact 3: vaccines given at birth
at_birth = df[df["due_age"].str.contains("birth", case=False)]
print("Fact 3:", len(at_birth), "vaccines are due at birth:", ", ".join(at_birth["vaccine"]))
