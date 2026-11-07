product = "TeekaTimer"
user = "A young mother in a village near Kopargaon"
problem = "Her 6-week-old son missed the 6-week anganwadi session. Is it too late?"
data_source = "MoHFW National Immunization Schedule and handbooks (mohfw.gov.in)"

print("=" * 55)
print(f"Product     : {product}")
print(f"User        : {user}")
print(f"Problem     : {problem}")
print(f"Data source : {data_source}")
print("=" * 55)

name = input("Your name: ")
question = input("Ask a vaccine question: ")
print(f"Hello {name}! You asked: {question}")
print("TeekaTimer will answer this from official MoHFW data.")