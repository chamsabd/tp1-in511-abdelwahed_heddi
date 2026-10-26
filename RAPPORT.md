# Rapport TP Agents IA

Binôme : Chams Abdelwahed et Ghada Heddi

## Exercices

### EX 1.1 


**Q** Est-ce que l'analyse contenue dans reasoning_content est correcte ?

Oui. Le modèle a bien compris la question. Il a choisi le bon outil (`Calculator`) avec les bons paramètres (`operation=multiply`, `a=15`, `b=8`).
```json
{
    "reasoning_content": "
    1. **Analyze the Request:**
     The user is asking for the result of \"15 times 8\". This is a simple multiplication task.

     2. **Examine Available Tools:** The available tool is `Calculator`, which can perform basic mathematical operations: add, subtract, multiply, divide.
     

3. **Determine the Appropriate Tool and Parameters:**
    * The request is multiplication ($15 \\times 8$).
    * The `Calculator` tool has an `operation` parameter (which should be 'multiply') and two operands, `a` and `b`.
    * `a` = 15
    * `b` = 8
    * `operation` = \"multiply\"


     4. **Construct the Tool Call:**```json
   {
     \"tool_name\": \"Calculator\",
     \"arguments\": {
       \"operation\": \"multiply\",
       \"a\": 15,
       \"b\": 8
     }
   }```

     5. **Formulate the Response:** Generate the tool call to execute the calculation. (Self-correction: Ensure the output format matches the expected tool call structure.)"
}
```
**Q**  Que contient le champ tool_calls dans la réponse du LLM ?

Il contient la demande d'appel d'outil du LLM :
- le type d'appel (`function`)
- le nom de l'outil
- les arguments sérialisés en JSON
- un identifiant d'appel (`id`) qui servira ensuite à relier la réponse de l'outil
```json
{
    "tool_calls": [
    {
            "type": "function",
            "function": {
                "name": "Calculator",
                "arguments": "{\"a\":15,\"b\":8,\"operation\":\"multiply\"}"
            },
            "id": "QhKMvfkQywqLUqsr4AG6v1Y18fkDrdB8"
    }
    ]
}
```
**Q** Pourquoi le LLM a-t-il choisi d'appeler Calculator plutôt que de répondre directement ?

Parce que l'outil est explicitement disponible et adapté à la tâche. Le LLM peut répondre directement, mais il privilégie souvent l'outil pour produire une réponse plus fiable et conforme au protocole.

**Q** Que se passe-t-il si vous ne transmettez pas l'argument tools à call_llm ?

Le LLM n'a plus la liste des outils, donc il répond directement en texte.

### EX 1.2

**Q** Pourquoi faut-il ajouter la réponse du LLM (`message`) avant le résultat de l'outil ?


Sans historique :
```json

    "messages": [
        {
            "role": "user",
            "content": "What is 15 times 8?"
        },
        {
            "role": "tool",
            "tool_call_id": "cF5pzYFHhUvBeRixpyXJP7yOjGYcZP7M",
            "content": "120"
        }
    ],
    "response": {
        "role": "assistant",
        "content": "",
        "tool_calls": [
            {
                "type": "function",
                "function": {
                    "name": "Calculator",
                    "arguments": "{\"a\":15,\"b\":8,\"operation\":\"multiply\"}"
                },
                "id": "OhILsO8OJ4GrFIeT7waVbJfGBbCAEGwG"
            }
        ]
    }


```
Dans ce test, le LLM n'a pas donné le résultat final. Il a redemandé un appel d'outil (`tool_calls` présent), car il ne peut pas relier le message `tool` à un appel assistant précis (il manque l'historique juste avant).

Il faut garder le bon ordre :
1. message assistant qui contient `tool_calls`,
2. message(s) `tool` avec `tool_call_id` correspondant.

Sinon, l'API ne peut pas relier correctement le message `tool` à une demande précédente de l'assistant. Le modèle repart donc sur un nouvel appel d'outil, au lieu de donner la réponse finale.

**Q** Quel est le rôle du champ `tool_call_id` ?

Il sert à relier le résultat d'un outil à un appel précis de l'assistant

**Q** Que se passe-t-il si vous oubliez d'ajouter le résultat de l'outil à l'historique ?

On obtient une erreur (`400 Bad Request`) au prochain appel LLM.

Si on n'ajoute pas le message `role: tool`, l'échange est incomplet , parce que l'assistant a demandé un outil mais na pas reçu le message tool correspondant.

### EX 1.3

**Q** Comment le LLM sait-il quels sont les paramètres de l'outil ? 

`make_tools` transforme la dataclass en schéma JSON (nom, description, paramètres, types, champs obligatoires). Le LLM lit ce schéma pour savoir quoi remplir.

**Q** Que se passe-t-il si vous ajoutez un champ avec une valeur par défaut ?

Le champ apparaît dans `properties` avec sa valeur `default`,mais non pas dans `required`. Donc ce paramètre devient optionnel.
Exemple :
```json
{
    "properties": {
        "text": {
            "type": "string"
        },
        "countPunctuationCharacters": {
            "type": "boolean",
            "default": false
        }
    },
    "required": [
        "text"
    ]
}

```
LLM reasoning :
```json
..The available tool is `WordCounter`, which takes a `text` argument and returns the number of words....
`countPunctuationCharacters`: (Optional)...
'tool_calls': [{'type': 'function', 'function': {'name': 'WordCounter', 'arguments': '{"text":"Hello world, this is a test"}'}, 'id': 'EthIYXZnszpppEXNwPyHNoF3yLUMPakn'}]
```
Donc le LLM a bien lu qu'il y a un paramètre optionnel et il l'ignore puisqu'il contient déjà une valeur.
Dans d'autres cas, le LLM peut aussi remplir ce paramètre si c'est utile.

**Q** Pouvez-vous ajouter un champ `Literal["french", "english"]` pour restreindre les valeurs possibles ?

Oui, on peut l'ajouter, et cela est exporté en pratique comme une contrainte de type enum dans le schéma.

Exemple de sortie LLM (extrait) :
```json
"language" (required): The language of the text (e.g., "english" or "french")
```

Ici, le LLM a lu `english` et `french` comme des exemples, et non comme les seules valeurs possibles. C'est pour cela que j'ai aussi testé `spanish`.

Dans ce cas,selon notre raisonement le LLM doit bloquer l'appel ou renvoyer une erreur.

Donc j'ai testé avec une autre langue pour savoir ce qu'il peut répondre dans ce cas :
```json
`language`: The text is mixed (Spanish and English words), but the primary language seems to be Spanish. I should specify the language for accuracy. Let's try 'spanish'.
...
'tool_calls': [{'type': 'function', 'function': {'name': 'WordCounter', 'arguments': '{"language":"spanish","text":"Hola mundo, esto es una prueba"}'},....
```
Conclusion : `Literal` aide le modèle, mais ne garantit pas 100 % du respect. Il faut garder une validation stricte dans le code.

### EX 2.1
Résultats obtenus :
```json
Question: What is 15 times 8?
Nombre d'itérations: 2
Résultat: The answer is 120.

Historique: [{'role': 'system', 'content': 'You are a calculator assistant.
Use the Calculator tool when the user asks for arithmetic operations.

'}, {'role': 'user', 'content': 'What is 15 times 8?'}, {'role': 'assistant', 'content': '', 'reasoning_content': '1.  **Analyze the user request:** The user is asking "What is 15 times 8?".
2.  **Identify the required tool:** This is an arithmetic operation (multiplication). The `Calculator` tool is suitable for this task.
3.  **Determine the tool parameters:**
    *   `operation`: The user asked for "times", which corresponds to the `multiply` operation.
    *   `a`: The first number is 15.
    *   `b`: The second number is 8.
4.  **Formulate the tool call:** `Calculator(operation=\'multiply\', a=15, b=8)`
5.  **Execute the tool call (mental simulation/actual call):** The tool will calculate $15 \\times 8 = 120$.
6.  **Format the final answer:** State the result clearly to the user.', 'tool_calls': [{'type': 'function', 'function': {'name': 'Calculator', 'arguments': '{"a":15,"b":8,"operation":"multiply"}'}, 'id': 'Dsy8rVvZyy6GKeZlXz3HUfyiiVRjPoqd'}]}, {'role': 'tool', 'tool_call_id': 'Dsy8rVvZyy6GKeZlXz3HUfyiiVRjPoqd', 'content': '120'}, {'role': 'assistant', 'content': 'The answer is 120.'}]

---
Question: What is 5 times 8?
Nombre d'itérations: 2
Résultat: The answer is 40.

Historique: [{'role': 'system', 'content': 'You are a calculator assistant.
Use the Calculator tool when the user asks for arithmetic operations.

'}, {'role': 'user', 'content': 'What is 5 times 8?'}, {'role': 'assistant', 'content': '', 'reasoning_content': '1. **Analyze the user request:** The user is asking "What is 5 times 8?". This is a request for a basic arithmetic operation (multiplication).

2. **Examine the available tools:** The `Calculator` tool is available, which supports `add`, `subtract`, `multiply`, and `divide`.

3. **Determine the appropriate tool:** The request "5 times 8" maps directly to the `multiply` operation in the `Calculator` tool.

4. **Identify the parameters:**
    * `a`: 5
    * `b`: 8
    * `operation`: "multiply"

5. **Construct the tool call:** Call `Calculator` with these parameters.

6. **Formulate the response:** Generate the tool call. (Self-correction: Do not execute the tool yet; just output the tool call in the required format.)', 'tool_calls': [{'type': 'function', 'function': {'name': 'Calculator', 'arguments': '{"a":5,"b":8,"operation":"multiply"}'}, 'id': 'h4eekwgFWcOJMS7VGxVZ7SffsDoZ6O6H'}]}, {'role': 'tool', 'tool_call_id': 'h4eekwgFWcOJMS7VGxVZ7SffsDoZ6O6H', 'content': '40'}, {'role': 'assistant', 'content': 'The answer is 40.'}]

---
Question: What is 15 plus 8?
Nombre d'itérations: 2
Résultat: 

Historique: [{'role': 'system', 'content': 'You are a calculator assistant.
Use the Calculator tool when the user asks for arithmetic operations.

'}, {'role': 'user', 'content': 'What is 15 plus 8?'}, {'role': 'assistant', 'content': '', 'reasoning_content': '1. **Analyze the user request:** The user is asking for the result of the arithmetic operation "15 plus 8".

2. **Identify the appropriate tool:** The request involves a mathematical operation (addition). The available tool `Calculator` is designed for performing such operations.

3. **Determine the tool parameters:**
    * The operation is addition (`operation="add"`).
    * The first number is 15 (`a=15`).
    * The second number is 8 (`b=8`).

4. **Construct the tool call:** `Calculator(operation="add", a=15, b=8)`

5. **Generate the output:** Present the tool call to the user.', 'tool_calls': [{'type': 'function', 'function': {'name': 'Calculator', 'arguments': '{"a":15,"b":8,"operation":"add"}'}, 'id': '5RuBxHdXOF6pYZfK7d05Aidpq7wiAOJe'}]}, {'role': 'tool', 'tool_call_id': '5RuBxHdXOF6pYZfK7d05Aidpq7wiAOJe', 'content': '23'}, {'role': 'assistant', 'content': ''}]
```

## EX 2.3
Nous avons testé les variantes A et B .

**Q** Quelle variante produit les meilleures réponses ?

Il n'y a pas une variante toujours meilleure.
- Variante A peut réduire le nombre de requêtes avec des jointures (donc moins d'itérations et moins de coût).

- Variante B aide surtout quand la requête SQL est fausse : le modèle corrige l'erreur avant de continuer.

**Q** Le prompt influence-t-il le nombre d'itérations ? 

Oui. Le prompt change la façon de résoudre la question, donc aussi le nombre d'itérations. Par exemple, le LLM peut lancer deux outils dans la même itération :
```txt
  [iter 2] DescribeTable table=books
             -> 8 rows
  [iter 2] DescribeTable table=publishers
             -> 4 rows
```
Il peut aussi faire moins d'itérations en écrivant directement une requête SQL avec `JOIN`.

**Q** Peut-on demander au LLM de "penser étape par étape" (chain-of-thought) ?

Oui, mais ici c'est déjà dans la prompt de base :

```txt
Think step by step. Explore the schema first, then query.
```

Donc la variante C (`Explain your reasoning before each tool call`) n'ajoute pas une vraie instruction supplémentaire. Elle répète la même consigne, mais sous une forme plus longue.

En pratique, cela ne donne pas un gain réel sur la qualité. Ça augmente seulement la consommation de tokens et ajoute du bruit textuel. Le modèle suit déjà l'ordre logique attendu : regarder le schéma, choisir une table, puis faire la requête.

## EX 3 Extension A - Guardrails de sécurité

**Q**  Pourquoi le mode read-only ne suffit-il pas ?

Le mode read-only bloque l'écriture dans la base, mais ce n'est pas suffisant à lui seul.
On ajoute aussi un filtre SQL pour :
- avoir une double sécurité (même si la config change par erreur),
- éviter des essais inutiles du LLM (moins d'erreurs et moins de coût),
- dire clairement la règle : cet agent est en lecture uniquement.

**Q**  Comment un attaquant pourrait-il contourner un blocage par mots-clés ?

Un simple blocage par mots-clés peut être contourné avec des variantes d'écriture SQL, par exemple :
- commentaires et masquage (`UP/**/DATE`, espaces spéciaux),
- encodages/concaténations ou constructions SQL plus complexes,
- requêtes multi-statements ou sous-requêtes qui échappent à un filtre naïf.



**Q**  Existe-t-il des bibliothèques pour parser et valider du SQL ?

Oui. Exemples utiles en Python (selon une recherche internet) :
- `sqlglot` : lecture et analyse de la structure SQL
- `sqlparse` : lecture et formatage SQL 

---
## Difficultés rencontrées

- Interpréter les logs trop longs, surtout quand l'historique est long et qu'il faut repérer le bon ordre des messages et des appels d'outils.
- Analyser les réponses du LLM dans l'EX 2.3, car même sans changement réel dans le code, le modèle peut changer son raisonnement, donc aussi sa réponse finale et le nombre d'itérations.

## Démarche suivie

- Lecture de `utils/data.py` et `utils/tools.py` pour comprendre le schéma de la base et la structure des outils.
- Implémentation étape par étape les algorithmes et les schémas donnés par le professeur.
- Ajout de logs plus lisibles pour visualiser l'outil appelé, ses paramètres, et un résumé du résultat.

## Solutions apportées et résultats

- Ex 1.1 : outil `Calculator` bien détecté et appelé par le LLM.
- Ex 1.2 : exécution de l'outil via `execute_tool`, chaînage correct des messages,
- Ex 1.3 : création d'un outil personnalisé (`WordCounter`) et test des paramètres optionnels/contraints.
- Ex 2.1/2.2 : boucle agent complète fonctionnelle avec limite d'itérations et appels SQL opérationnels.
- Ex 2.3 : comparaison de prompts montrant un impact du prompt sur coût, robustesse et nombre d'itérations.

## Réflexions

**Q**  Que pensez-vous du mécanisme de tool calling ?

**R** Le mécanisme de tool calling guide le raisonnement du modèle en lui imposant un cadre d’action et en contraignant le format de sortie. Le LLM n’est pas totalement libre de répondre dans n’importe quel style : il doit choisir un outil adapté puis produire une commande structurée, ce qui améliore la fiabilité et la cohérence de l’exécution



**Q** Quels sont les risques de sécurité d'un agent SQL ?

**R** Les risques sont plus larges que "une requête DELETE". Un agent SQL peut provoquer :
  - exécution de requêtes destructrices ou non autorisées ;
  - fuite d'informations sensibles si le modèle est libre d'accéder à toutes les tables ;
  - injection SQL par variantes de syntaxe, sous-requêtes, commentaires, concaténations ou requêtes multi-statements ;
  - surconsommation de ressources avec des requêtes lourdes ou des boucles de retry.


**Q** Comment améliorer la gestion du contexte ?

**R** Pour améliorer la gestion du contexte, on peut adopter une politique de mémoire adaptative : garder uniquement les X derniers messages, résumer les échanges anciens avec un modèle dédié, et utiliser un mécanisme de RAG pour stocker les informations utiles à long terme comme le schéma de la base, les règles métier ou les requêtes fréquemment utilisées. Cela permet de réduire le coût token, limiter la latence et préserver la qualité du raisonnement sans surcharger le contexte du modèle

**Q**  Quelles fonctionnalités vous sembleraient intéressantes d'ajouter ?

**R** Si nous avions plus de temps, nous aimerions tester un système multi-agents (Extension D), où un agent planifie la requête, un autre exécute l’accès SQL, et éventuellement un agent de validation contrôle la sécurité et la cohérence de la réponse. Nous aimerions aussi étudier les prompt injection attacks, car ils sont un risque important pour les agents qui manipulent des outils et des bases de données : une instruction cachée dans un message utilisateur ou dans une donnée externe peut essayer de détourner le comportement autorisé du système.



## Annexe
### Code Ex 2.2 : sqlite_agent.py
```py
import json
from utils import Database, make_sql_tools, make_tools, make_registry, call_llm, execute_tool

# Prompt système de base de l'énoncé
SYSTEM_PROMPT = """You are a SQL assistant with access to a SQLite database.

Tools:
- ListTables: list all tables
- DescribeTable: get table structure
- SQLQuery: execute any SQL query

Think step by step. Explore the schema first, then query."""


def extract_message(response):
    """Extrait le message du LLM de la réponse brute de l'API"""
    return response["choices"][0]["message"]


def run_agent(question, tool_classes, system_prompt=SYSTEM_PROMPT,
              max_iterations=5, verbose=True):
    """Boucle agent : LLM -> outils -> LLM -> ... -> réponse finale."""
    # Schémas JSON des outils (vus par le LLM) et registre nom -> classe
    tools = make_tools(tool_classes)
    registry = make_registry(tool_classes)

    # Historique initial : consigne système + question
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question},
    ]

    for i in range(max_iterations):  # limite anti-boucle infinie
        # Appel du LLM, puis ajout de sa réponse à l'historique
        message = extract_message(call_llm(messages, tools=tools))
        messages.append(message)

        # Pas de tool_calls : réponse finale
        tool_calls = message.get("tool_calls")
        if not tool_calls:
            return message["content"]

        # Sinon : exécution de chaque outil demandé
        for tool_call in tool_calls:
            try:
                result = execute_tool(tool_call, registry)
            except Exception as e:
                # L'erreur est renvoyée au LLM au lieu d'arrêter l'agent
                result = json.dumps({"error": str(e)})
            if verbose:
                print(f"  [iter {i + 1}] {tool_call['function']['name']} -> {result[:150]}")
            # Résultat lié à l'appel d'origine par tool_call_id
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "content": result,
            })

    return "Max iterations reached"


if __name__ == "__main__":
    db = Database("library.db")          # crée la base de démo si absente
    sql_tools = make_sql_tools(db)       # SQLQuery, ListTables, DescribeTable

    questions = [
        "What are the books written after 1970?",
        "Who is the author of 'Dune' and when were they born?",
        "How many books are there per genre?",
        "What is the average rating per publisher?",
        "Which author has written the most books?",
    ]
    for q in questions:
        print(f"
Q: {q}")
        print("A:", run_agent(q, sql_tools))
```
```txt
Exemple de sortie :
Q: What are the books written after 1970?
  [iter 1] ListTables -> ["authors", "publishers", "books"]
  [iter 2] DescribeTable -> [{"cid": 0, "name": "id", "type": "INTEGER", "notnull": 0, "dflt_value": null, "pk": 1}, {"cid": 1, "name": "title", "type": "TEXT", "notnull": 1, "df
  [iter 3] SQLQuery -> [{"title": "The Dispossessed"}, {"title": "Children of Dune"}, {"title": "Kindred"}, {"title": "Parable of the Sower"}, {"title": "Neuromancer"}, {"ti
A: The books written after 1970 are:
* The Dispossessed
* Children of Dune
* Kindred
* Parable of the Sower
* Neuromancer
* Snow Crash
* The Three-Body Problem....
```

