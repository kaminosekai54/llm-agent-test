configs = {}

configs["agents"] = {
"headManagerAgent":
{
"model":"mixtrale_groq",
},
"pubmedDataCollectorAgent":
{
"model":"llama3_groq",
},

"pubmedDataSearcherAgent":
{
"model":"llama3_groq",
},
}

def getConfigs():
    return configs