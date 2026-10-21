# Rapport TP Agents IA

Binôme : Chams Abdelwahed et Ghada Heddi 

## Exercices

### EX 1.1 


- Est-ce que l'analyse contenue dans reasoning_content est correcte ?

Oui, il a bien compris la question, a correctement identifié l’outil à utiliser et a déterminé comment l’appeler, notamment en précisant les arguments nécessaires.
```JSON
{'reasoning_content': 
'1. **Analyze the Request:** The user is asking for the result of "15 times 8". This is a simple multiplication task.\n\n
2. **Examine Available Tools:** The available tool is `Calculator`, which can perform basic mathematical operations: add, subtract, multiply, divide.\n\n

3. **Determine the Appropriate Tool and Parameters:**\n    * The request is multiplication ($15 \\times 8$).\n    * The `Calculator` tool has an `operation` parameter (which should be \'multiply\') and two operands, `a` and `b`.\n    * `a` = 15\n    * `b` = 8\n    * `operation` = "multiply"\n\n
4. **Construct the Tool Call:**\n   ```json\n   {\n     "tool_name": "Calculator",\n     "arguments": {\n       "operation": "multiply",\n       "a": 15,\n       "b": 8\n     }\n   }\n   ```\n\n

5. **Formulate the Response:** Generate the tool call to execute the calculation. (Self-correction: Ensure the output format matches the expected tool call structure.)'
}
```
- Que contient le champ tool_calls dans la réponse du LLM ?

Il contient la demande du LLM, c'est-à-dire l'outil à appeler ainsi que les arguments à lui transmettre.
```JSON
'tool_calls': [
    {
        'type': 'function',
        'function': {
            'name': 'Calculator',
            'arguments': '{"a":15,"b":8,"operation":"multiply"}'
        },
        'id': 'QhKMvfkQywqLUqsr4AG6v1Y18fkDrdB8'
    }
]
```
- Pourquoi le LLM a-t-il choisi d'appeler Calculator plutôt que de répondre directement ?

Parce qu'on lui a fourni des outils. Il commence par évaluer les outils dont il dispose et se demande, en quelque sorte : « De quels outils est-ce que je dispose ? »

Puisqu'il a accès à un outil capable d'effectuer ce calcul, il peut choisir de l'utiliser plutôt que de réaliser lui-même le calcul.

- Que se passe-t-il si vous ne transmettez pas l'argument tools à call_llm ?

Le LLM effectuera le raisonnement et le calcul lui-même, sans pouvoir appeler l'outil Calculator via ce mécanisme.
### EX1.2
- Pourquoi faut-il ajouter la réponse du LLM (`message`) avant le résultat de l'outil ?
sans historique:
```JSON
{'role': 'assistant', 'content': '15 times 8 is 120.', 'reasoning_content': '1. **Analyze the Request:** The user is asking for the result of the multiplication "15 times 8".\n\n2. **Identify Necessary Tools:** The available tools include `Calculator` with operations: add, subtract, multiply, divide. This tool is suitable for multiplication.\n\n3. **Determine Tool Parameters:**\n    *   `operation`: The operation is multiplication.\n    *   `a`: One operand is 15.\n    *   `b`: The other operand is 8.\n\n4. **Formulate the Tool Call:** `Calculator(operation=\'multiply\', a=15, b=8)` (or similar structure based on the tool definition).\n\n5. **Execute the Tool Call (Mental Simulation):**\n    *   $15 \\times 8 = 120$.\n\n6. **Generate the Response:** State the answer based on the calculation. (The final response should be the direct answer, optionally referencing the tool use if the format requires it, but for this simple calculation, a direct answer is usually best).\n\n7. **Final Answer Construction:** The result of 15 times 8 is 120.'}
```
historique de conversation (pour ne pas refaire le reasoning )
- Quel est le rôle du champ `tool_call_id` ?
pour bien relier la resultat d'execution d'un tool a une demande precise donner par le llm 
- Que se passe-t-il si vous oubliez d'ajouter le résultat de l'outil à l'historique ?
je suis pas sure mais peut etre erreur :
parceque dans le message on va avoire role user, assistant , alors que normalment le llm lui a le role assistant donc pour lui il ne repond pas 
## Difficultés rencontrées

- ...

## Démarche suivie

- ...

## Solutions apportées et résultats

- ...

## Réflexions

- Que pensez-vous du mécanisme de tool calling ?
- Quels sont les risques de sécurité d'un agent SQL ?
- Comment améliorer la gestion du contexte ?
- Quelles fonctionnalités vous sembleraient intéressantes d'ajouter ?

