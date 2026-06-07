from MorphologicalAnalysis.FsmMorphologicalAnalyzer import FsmMorphologicalAnalyzer

fsm = FsmMorphologicalAnalyzer()

test_words = [
    "Mal", "Esef",
    "Var", "Mis",
    "Cay", "Lak",
    "Bun", "Lari",
    "Bilir", "Sinizm",
    "Kap", "Cami"
]

for word in test_words:
    parse = fsm.morphologicalAnalysis(word)
    print(f"\n{word}:")
    if parse.size() > 0:
        for i in range(min(3, parse.size())):
            analysis = parse.getFsmParse(i).transitionList()
            plus_count = analysis.count('+')
            print(f"  {analysis} (plus count: {plus_count})")
    else:
        print("  No analysis")