#we are using spacy for lingustic feature extraction from a text
import spacy
from spacy.lang.en import English
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
#'en_core_web_sm' is a small english pipeline trained on web written text.
nlp_model = spacy.load('en_core_web_sm')
#'sentencizer' it is used to detect boundary of sentence it uses simple rule based strategy

def appendChunk(original, chunk):
    return original + ' ' + chunk


def isRelationCandidate(token):
    deps = ["ROOT", "adj", "attr", "agent", "amod"]
    return any(subs in token.dep_ for subs in deps)

def isConstructionCandidate(token):
    deps = ["compound", "prep", "conj", "mod"]
    return any(subs in token.dep_ for subs in deps)

def processSubjectObjectPairs(tokens, sentence):
    subject = ''
    object = ''
    relation = ''
    subjectConstruction = ''
    objectConstruction = ''
    for token in tokens:
        # printToken(token)
        if "punct" in token.dep_:
            continue
        if isRelationCandidate(token):
            relation = appendChunk(relation, token.lemma_)
        if isConstructionCandidate(token):
            if subjectConstruction:
                subjectConstruction = appendChunk(subjectConstruction, token.text)
            if objectConstruction:
                objectConstruction = appendChunk(objectConstruction, token.text)
        if "subj" in token.dep_:
            subject = appendChunk(subject, token.text)
            subject = appendChunk(subjectConstruction, subject)
            subjectConstruction = ''
        if "obj" in token.dep_:
            object = appendChunk(object, token.text)
            object = appendChunk(objectConstruction, object)
            objectConstruction = ''
    #print (subject.strip(), ",", relation.strip(), ",", object.strip())
    return (subject.strip(), relation.strip(), object.strip(), sentence)

# triple extraction is being done here here we call nlp_model sentence it generates token of sentence and 
#we pass these token and sentence to processsubjectobjectpair function it return triple and given sentence
def processSentence(sentence):
    tokens = nlp_model(sentence)
    return processSubjectObjectPairs(tokens, sentence)

#here from triples we are generating knowledge graph and storing into pickle file
def createGraph(triples):
    G = nx.Graph()
    for triple in triples:
        
        if triple[3] not in G:
            G.add_node(triple[3])

        if triple[0] not in G:
            G.add_node(triple[0])
            G.add_edge(triple[0], triple[3])
            
        else: 
            print(triple[0])
            
        if triple[1] not in G:
            G.add_node(triple[1])
            G.add_edge(triple[1], triple[3])
            
        else:
            G.add_edge(triple[1], triple[3])
            print(triple[1])

        if triple[2] not in G:
            G.add_node(triple[2])
            G.add_edge(triple[2], triple[3])
        else:
            G.add_edge(triple[2], triple[3])
            print(triple[2])

    nx.write_gpickle(G, "test.gpickle")

#if we want to add graph in existed graph
def addGraph(G, triple):

    if triple[3] not in G:
            G.add_node(triple[3])

    if triple[0] not in G:
        G.add_node(triple[0])
        G.add_edge(triple[0], triple[3])
        
    else: 
        print(triple[0])
        
    if triple[1] not in G:
        G.add_node(triple[1])
        G.add_edge(triple[1], triple[3])
        
    else:
        G.add_edge(triple[1], triple[3])
        print(triple[1])

    if triple[2] not in G:
        G.add_node(triple[2])
        G.add_edge(triple[2], triple[3])
    else:
        G.add_edge(triple[2], triple[3])
        print(triple[2])
   
    nx.write_gpickle(G, "test.gpickle")

    return G

#unpickle the graph and store in G
def readGraph():
    G = nx.read_gpickle("test.gpickle")
    return G
#here we are printing the graph
def printGraph(G):
    
    pos = nx.spring_layout(G)
    plt.figure(figsize=(12, 8))
    nx.draw(G, pos, edge_color='black', width=1, linewidths=1,
    node_size=300, node_color='skyblue', alpha=0.9,
    labels={node: node for node in G.nodes()})
    plt.axis('off')
    plt.show()
    plt.savefig("output.png")
#this function return the extracted context from graph
def get_context(text):
    G = readGraph()
    #text = "How many credit hours are required for bachelor's degree"
    triple = processSentence(text)    
    three_matched = []
    two_matched = []
    single_matched = []
    for i in G.nodes.items():
        if triple[0] in i[0]:
            if i[0] not in single_matched and len(i[0]) > 30:
                single_matched.append(i[0])
            if triple[1] in i[0]:
                if i[0] not in two_matched and len(i[0]) > 30:
                    two_matched.append(i[0])
                    if i[0] in single_matched:
                        single_matched = single_matched[:-1]
                if triple[2] in i[0]:
                    if i[0] not in three_matched and len(i[0]) > 30:
                        three_matched.append(i[0])
                        if i[0] in two_matched:
                            two_matched = two_matched[:-1]
            
        if triple[1] in i[0]:
            if i[0] not in single_matched and len(i[0]) > 30:
                single_matched.append(i[0])
            if triple[2] in i[0]:
                if i[0] not in two_matched and len(i[0]) > 30:
                    two_matched.append(i[0])
                    if i[0] in single_matched:
                        single_matched = single_matched[:-1]
                if triple[0] in i[0]:
                    if i[0] not in three_matched and len(i[0]) > 30:
                        three_matched.append(i[0])
                        if i[0] in two_matched:
                            two_matched = two_matched[:-1]

        if triple[2] in i[0]:
            if i[0] not in single_matched and len(i[0]) > 30:
                single_matched.append(i[0])
            if triple[0] in i[0]:
                if i[0] not in two_matched and len(i[0]) > 30:
                    two_matched.append(i[0])
                    if i[0] in single_matched:
                        single_matched = single_matched[:-1]
                if triple[1] in i[0]:
                    if i[0] not in three_matched and len(i[0]) > 30:
                        three_matched.append(i[0])
                        if i[0] in two_matched:
                            two_matched = two_matched[:-1]


    context_3 = ".".join(three_matched)
    context_2 = ".".join(two_matched)
    context_1 = ".".join(single_matched)
    # print(context_3)
    # print(context_2)
    # print(context_1)
    context = context_3 +"."+ context_2 +"."+ context_1
    #print(context)
    return context


if __name__ == "__main__":
    # df = pd.read_csv("provided_data.csv")
    # sentences = df.to_numpy()
    # triples = []
    # # print (sentences)
    # for sentence in sentences:
    #     triples.append(processSentence(sentence[0]))
    # createGraph(triples)
    G = readGraph()
    printGraph(G)
    text = "How many credit hours are required for bachelor's degree"
    triple = processSentence(text)    
    three_matched = []
    two_matched = []
    single_matched = []
    for i in G.nodes.items():
        if triple[0] in i[0]:
            if i[0] not in single_matched and len(i[0]) > 30:
                single_matched.append(i[0])
            if triple[1] in i[0]:
                if i[0] not in two_matched and len(i[0]) > 30:
                    two_matched.append(i[0])
                    if i[0] in single_matched:
                        single_matched = single_matched[:-1]
                if triple[2] in i[0]:
                    if i[0] not in three_matched and len(i[0]) > 30:
                        three_matched.append(i[0])
                        if i[0] in two_matched:
                            two_matched = two_matched[:-1]
            
        if triple[1] in i[0]:
            if i[0] not in single_matched and len(i[0]) > 30:
                single_matched.append(i[0])
            if triple[2] in i[0]:
                if i[0] not in two_matched and len(i[0]) > 30:
                    two_matched.append(i[0])
                    if i[0] in single_matched:
                        single_matched = single_matched[:-1]
                if triple[0] in i[0]:
                    if i[0] not in three_matched and len(i[0]) > 30:
                        three_matched.append(i[0])
                        if i[0] in two_matched:
                            two_matched = two_matched[:-1]

        if triple[2] in i[0]:
            if i[0] not in single_matched and len(i[0]) > 30:
                single_matched.append(i[0])
            if triple[0] in i[0]:
                if i[0] not in two_matched and len(i[0]) > 30:
                    two_matched.append(i[0])
                    if i[0] in single_matched:
                        single_matched = single_matched[:-1]
                if triple[1] in i[0]:
                    if i[0] not in three_matched and len(i[0]) > 30:
                        three_matched.append(i[0])
                        if i[0] in two_matched:
                            two_matched = two_matched[:-1]

    context_3 = ".".join(three_matched)
    context_2 = ".".join(two_matched)
    context_1 = ".".join(single_matched)
    # print(context_3)
    # print(context_2)
    # print(context_1)
    context = context_3 +"."+ context_2 +"."+ context_1
    #print(context)
