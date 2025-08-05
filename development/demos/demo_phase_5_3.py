#!/usr/bin/env python3
"""
Comprehensive demo for Phase 5.3: Note Summarization & Connection Discovery
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.ai.summarizer import AISummarizer
from src.ai.connections import AIConnections
from src.ai.ollama_client import OllamaClient


def create_sample_notes():
    """Create sample notes for demonstration."""
    return {
        "ai_fundamentals.md": """---
type: permanent
created: 2025-01-15
tags: [ai, machine-learning, fundamentals]
---

# Artificial Intelligence Fundamentals

Artificial intelligence (AI) represents one of the most transformative technologies of our time. At its core, AI is the simulation of human intelligence processes by machines, particularly computer systems. These processes include learning (the acquisition of information and rules for using the information), reasoning (using rules to reach approximate or definite conclusions), and self-correction.

The field of AI encompasses several key areas including machine learning, where systems automatically improve their performance through experience; natural language processing, which enables computers to understand and generate human language; computer vision, allowing machines to interpret and understand visual information; and robotics, where AI controls physical systems to perform tasks.

Machine learning, a subset of AI, has become particularly prominent due to its practical applications. It involves algorithms that can learn patterns from data without being explicitly programmed for every scenario. Deep learning, a further subset of machine learning, uses neural networks with multiple layers to model and understand complex patterns in data.

The applications of AI are vast and growing, spanning healthcare diagnostics, autonomous vehicles, financial trading, recommendation systems, and scientific research. As AI systems become more sophisticated, they raise important questions about ethics, employment, privacy, and the future of human-machine interaction.

Understanding AI fundamentals is crucial for anyone working in technology today, as these systems increasingly influence how we work, communicate, and make decisions in our daily lives.
""",

        "deep_learning_overview.md": """---
type: literature
created: 2025-01-16
tags: [deep-learning, neural-networks, ai]
---

# Deep Learning: A Comprehensive Overview

Deep learning represents a revolutionary approach to machine learning that has transformed the field of artificial intelligence. Unlike traditional machine learning algorithms that require manual feature engineering, deep learning systems automatically discover the representations needed for feature detection or classification from raw data.

## Neural Network Architecture

Deep learning is based on artificial neural networks, particularly deep neural networks with multiple hidden layers. These networks are inspired by the structure and function of the human brain, consisting of interconnected nodes (neurons) that process and transmit information. Each connection has an associated weight that adjusts as learning proceeds, determining the importance of the input.

## Key Components

The fundamental building blocks of deep learning include:

- **Neurons**: Basic processing units that receive inputs, apply a transformation, and produce an output
- **Layers**: Collections of neurons that process information at the same level of abstraction
- **Activation Functions**: Mathematical functions that determine whether a neuron should be activated
- **Backpropagation**: The algorithm used to train neural networks by adjusting weights based on errors

## Applications and Impact

Deep learning has achieved remarkable success in various domains:

- **Computer Vision**: Image recognition, object detection, and medical imaging analysis
- **Natural Language Processing**: Language translation, sentiment analysis, and text generation
- **Speech Recognition**: Converting spoken language to text with high accuracy
- **Game Playing**: Achieving superhuman performance in complex games like Go and chess
- **Drug Discovery**: Accelerating the identification of potential therapeutic compounds

## Challenges and Limitations

Despite its successes, deep learning faces several challenges:

- **Data Requirements**: Deep networks typically require large amounts of labeled training data
- **Computational Resources**: Training deep models demands significant computational power
- **Interpretability**: Deep networks often function as "black boxes," making it difficult to understand their decision-making process
- **Overfitting**: Models may perform well on training data but poorly on new, unseen data

## Future Directions

The field continues to evolve with emerging techniques such as transformer architectures, attention mechanisms, and few-shot learning. Researchers are working on making deep learning more efficient, interpretable, and applicable to domains with limited data.

As deep learning technology matures, it promises to unlock new possibilities in artificial intelligence while addressing current limitations through continued research and innovation.
""",

        "quantum_computing_basics.md": """---
type: permanent
created: 2025-01-17
tags: [quantum-computing, physics, technology]
---

# Quantum Computing Fundamentals

Quantum computing represents a paradigm shift from classical computing, leveraging the principles of quantum mechanics to process information in fundamentally different ways. While classical computers use bits that exist in definite states of 0 or 1, quantum computers use quantum bits (qubits) that can exist in superposition states, being both 0 and 1 simultaneously.

## Core Principles

The power of quantum computing stems from three key quantum mechanical phenomena:

**Superposition**: Qubits can exist in multiple states simultaneously, allowing quantum computers to explore many possible solutions to a problem at once. This parallelism grows exponentially with the number of qubits.

**Entanglement**: Qubits can be correlated in ways that have no classical analog. When qubits are entangled, measuring one instantly affects the others, regardless of the distance between them.

**Interference**: Quantum algorithms manipulate probability amplitudes so that correct answers are amplified while incorrect ones cancel out through destructive interference.

## Quantum Algorithms

Several quantum algorithms demonstrate potential advantages over classical approaches:

- **Shor's Algorithm**: Efficiently factors large integers, threatening current cryptographic systems
- **Grover's Algorithm**: Searches unsorted databases quadratically faster than classical methods
- **Quantum Simulation**: Models quantum systems that are intractable for classical computers

## Current Challenges

Quantum computing faces significant technical hurdles:

**Quantum Decoherence**: Quantum states are extremely fragile and easily disrupted by environmental interference, limiting computation time.

**Error Rates**: Current quantum computers have high error rates, requiring quantum error correction techniques that demand many physical qubits for each logical qubit.

**Scalability**: Building quantum computers with enough stable qubits for practical applications remains challenging.

## Applications and Future

Potential applications include:
- Cryptography and security
- Drug discovery and molecular modeling  
- Financial modeling and optimization
- Machine learning and artificial intelligence
- Climate modeling and materials science

While practical quantum computers for general use may still be years away, the field continues to advance rapidly with increasing investment from governments and technology companies worldwide.
""",

        "cooking_italian_pasta.md": """---
type: permanent
created: 2025-01-18
tags: [cooking, italian, pasta, recipes]
---

# The Art of Italian Pasta Cooking

Italian pasta cooking is both an art and a science, requiring attention to technique, timing, and quality ingredients. Mastering the fundamentals of pasta preparation opens the door to countless delicious possibilities in Italian cuisine.

## Choosing the Right Pasta

Different pasta shapes serve different purposes:

- **Long pasta** (spaghetti, linguine, fettuccine): Best with oil-based or cream sauces
- **Short pasta** (penne, rigatoni, fusilli): Ideal for chunky sauces that can be trapped in the shapes
- **Stuffed pasta** (ravioli, tortellini): Pairs well with simple butter or light tomato sauces

## The Perfect Cooking Technique

**Water Preparation**: Use a large pot with plenty of water (at least 4 quarts per pound of pasta). Add salt generously - the water should taste like seawater.

**Timing**: Start the sauce before cooking the pasta. Fresh pasta cooks in 2-4 minutes, while dried pasta typically takes 8-12 minutes.

**Al Dente**: Cook pasta until it's firm to the bite. It should have a slight resistance when chewed but not be crunchy.

**Reserve Pasta Water**: Save a cup of the starchy cooking water before draining. This liquid gold helps bind sauces to pasta.

## Classic Sauce Pairings

**Aglio e Olio**: Spaghetti with garlic, olive oil, and red pepper flakes - simplicity at its finest.

**Carbonara**: Eggs, pecorino cheese, guanciale, and black pepper create this Roman classic.

**Marinara**: A simple tomato sauce with garlic, basil, and olive oil that showcases quality ingredients.

**Pesto**: Basil, pine nuts, garlic, parmesan, and olive oil blended into a vibrant green sauce.

## Essential Tips

- Never rinse pasta after cooking unless making a cold salad
- Always finish cooking pasta in the sauce for the last minute
- Use high-quality ingredients - they make a significant difference
- Grate cheese fresh for the best flavor and texture
- Taste and adjust seasoning throughout the cooking process

Mastering these fundamentals will elevate your pasta dishes from good to exceptional, bringing authentic Italian flavors to your kitchen.
""",

        "travel_japan_guide.md": """---
type: literature
created: 2025-01-19
tags: [travel, japan, culture, guide]
---

# Essential Guide to Traveling in Japan

Japan offers a unique blend of ancient traditions and cutting-edge modernity, making it one of the world's most fascinating travel destinations. This guide covers essential information for first-time visitors to navigate Japanese culture and customs successfully.

## Cultural Etiquette

Understanding Japanese etiquette is crucial for respectful travel:

**Bowing**: A slight bow shows respect. The depth and duration depend on the situation's formality.

**Shoes**: Remove shoes when entering homes, temples, and some restaurants. Look for shoe racks or slippers at entrances.

**Chopstick Etiquette**: Never stick chopsticks upright in rice or pass food chopstick-to-chopstick, as these actions are associated with funeral rites.

**Public Behavior**: Keep conversations quiet on public transportation, avoid eating while walking, and don't blow your nose in public.

## Transportation

Japan's transportation system is efficient but can be complex:

**JR Pass**: The Japan Rail Pass offers unlimited travel on JR trains, including most shinkansen (bullet trains), for foreign tourists.

**IC Cards**: Suica or Pasmo cards work for trains, subways, buses, and many shops throughout the country.

**Punctuality**: Trains run exactly on schedule. Being late is considered disrespectful.

## Accommodation Options

**Ryokan**: Traditional inns offering tatami rooms, futon beds, and often include kaiseki meals and onsen (hot springs).

**Business Hotels**: Compact, efficient rooms with modern amenities, perfect for budget-conscious travelers.

**Capsule Hotels**: Unique pod-style accommodation popular in major cities.

## Food Culture

Japanese cuisine extends far beyond sushi:

**Ramen**: Regional varieties offer different broths, noodles, and toppings.

**Izakaya**: Casual pubs serving small plates and drinks, perfect for experiencing local atmosphere.

**Convenience Store Food**: 7-Eleven and Lawson offer surprisingly high-quality meals and snacks.

**Seasonal Specialties**: Japanese cuisine emphasizes seasonal ingredients and presentation.

## Must-Visit Destinations

**Tokyo**: Modern metropolis with districts like Shibuya, Harajuku, and Asakusa each offering distinct experiences.

**Kyoto**: Former capital with over 2,000 temples and shrines, traditional architecture, and geisha districts.

**Osaka**: Known as "Japan's kitchen" for its exceptional food culture and friendly locals.

**Mount Fuji**: Japan's iconic mountain, best viewed from the Fuji Five Lakes region.

## Practical Tips

- Learn basic Japanese phrases - locals appreciate the effort
- Carry cash, as many places don't accept credit cards
- Download translation apps for restaurant menus and signs
- Respect photography rules, especially in temples and with people
- Purchase a pocket WiFi device or SIM card for internet access

Japan rewards travelers who approach it with curiosity, respect, and openness to new experiences.
"""
    }


def demo_summarization():
    """Demonstrate note summarization capabilities."""
    print("🔍 PHASE 5.3 DEMO: NOTE SUMMARIZATION")
    print("=" * 60)
    
    # Initialize summarizer
    summarizer = AISummarizer(min_length=300)  # Lower threshold for demo
    
    # Check if Ollama is available
    client = OllamaClient()
    if not client.health_check():
        print("⚠️  Ollama service not available - using extractive summarization only")
        print()
    
    sample_notes = create_sample_notes()
    
    for filename, content in sample_notes.items():
        print(f"📄 Processing: {filename}")
        word_count = len(content.split())
        print(f"   Original length: {word_count} words")
        
        if summarizer.should_summarize(content):
            print("   🤖 Generating summaries...")
            
            # Try abstractive summary first
            if client.health_check():
                try:
                    abstractive = summarizer.generate_summary(content, "abstractive")
                    if abstractive:
                        abs_words = len(abstractive.split())
                        compression = abs_words / word_count
                        print(f"   ✅ Abstractive summary: {abs_words} words ({compression:.1%} of original)")
                        print(f"      Preview: {abstractive[:100]}...")
                except Exception as e:
                    print(f"   ❌ Abstractive failed: {e}")
            
            # Generate extractive summary
            extractive = summarizer.generate_extractive_summary(content)
            if extractive:
                ext_words = len(extractive.split())
                compression = ext_words / word_count
                print(f"   ✅ Extractive summary: {ext_words} words ({compression:.1%} of original)")
                print(f"      Preview: {extractive[:100]}...")
        else:
            print("   ℹ️  Note too short for summarization")
        
        print()


def demo_connections():
    """Demonstrate connection discovery capabilities."""
    print("🔗 PHASE 5.3 DEMO: CONNECTION DISCOVERY")
    print("=" * 60)
    
    # Initialize connections system
    connections = AIConnections(similarity_threshold=0.6, max_suggestions=3)
    
    # Check if Ollama is available
    client = OllamaClient()
    if not client.health_check():
        print("⚠️  Ollama service not available - using simple text similarity")
        print()
    
    sample_notes = create_sample_notes()
    
    # Demo 1: Find similar notes to AI fundamentals
    target_note = "ai_fundamentals.md"
    print(f"🎯 Finding notes similar to: {target_note}")
    
    # Create corpus excluding target note
    corpus = {k: v for k, v in sample_notes.items() if k != target_note}
    target_content = sample_notes[target_note]
    
    try:
        similar_notes = connections.find_similar_notes(target_content, corpus)
        
        if similar_notes:
            print(f"   ✅ Found {len(similar_notes)} similar notes:")
            for i, (filename, similarity) in enumerate(similar_notes, 1):
                print(f"   {i}. {filename} (similarity: {similarity:.1%})")
        else:
            print("   ℹ️  No similar notes found above threshold")
    except Exception as e:
        print(f"   ❌ Error finding similar notes: {e}")
    
    print()
    
    # Demo 2: Generate link suggestions
    print(f"🔗 Generating link suggestions for: {target_note}")
    
    try:
        suggestions = connections.suggest_links(target_content, corpus)
        
        if suggestions:
            print(f"   ✅ Generated {len(suggestions)} link suggestions:")
            for i, suggestion in enumerate(suggestions, 1):
                print(f"   {i}. [[{suggestion['filename']}]]")
                print(f"      Reason: {suggestion['reason']}")
        else:
            print("   ℹ️  No link suggestions found")
    except Exception as e:
        print(f"   ❌ Error generating suggestions: {e}")
    
    print()
    
    # Demo 3: Build connection map
    print("🗺️  Building connection map for all notes...")
    
    try:
        connection_map = connections.build_connection_map(sample_notes)
        
        # Calculate statistics
        total_connections = sum(len(conns) for conns in connection_map.values())
        connected_notes = sum(1 for conns in connection_map.values() if conns)
        avg_connections = total_connections / len(sample_notes) if sample_notes else 0
        
        print(f"   ✅ Connection map built successfully!")
        print(f"   📊 Statistics:")
        print(f"      Total notes: {len(sample_notes)}")
        print(f"      Connected notes: {connected_notes}")
        print(f"      Total connections: {total_connections}")
        print(f"      Average connections per note: {avg_connections:.1f}")
        
        # Show most connected notes
        sorted_notes = sorted(connection_map.items(), key=lambda x: len(x[1]), reverse=True)
        print(f"   🔗 Most connected notes:")
        for filename, connections_list in sorted_notes[:3]:
            if connections_list:
                print(f"      {filename}: {len(connections_list)} connections")
        
    except Exception as e:
        print(f"   ❌ Error building connection map: {e}")


def main():
    """Run the comprehensive Phase 5.3 demo."""
    print("🚀 PHASE 5.3: NOTE SUMMARIZATION & CONNECTION DISCOVERY")
    print("🎯 Advanced AI Features for InnerOS Zettelkasten")
    print("=" * 60)
    print()
    
    # Check Ollama availability
    client = OllamaClient()
    if client.health_check():
        print("✅ Ollama service is available - full AI features enabled")
    else:
        print("⚠️  Ollama service not available - using fallback methods")
    print()
    
    # Run demonstrations
    demo_summarization()
    print()
    demo_connections()
    
    print("=" * 60)
    print("🎉 Phase 5.3 Demo Complete!")
    print()
    print("📚 Features Demonstrated:")
    print("   ✅ Abstractive summarization (AI-powered)")
    print("   ✅ Extractive summarization (keyword-based)")
    print("   ✅ Semantic similarity detection")
    print("   ✅ Link suggestion generation")
    print("   ✅ Connection map building")
    print("   ✅ YAML frontmatter handling")
    print("   ✅ Graceful error handling")
    print()
    print("🛠️  CLI Tools Available:")
    print("   • python3 src/cli/summarizer_demo.py <file>")
    print("   • python3 src/cli/connections_demo.py similar <target> <corpus_dir>")
    print("   • python3 src/cli/connections_demo.py links <target> <corpus_dir>")
    print("   • python3 src/cli/connections_demo.py map <corpus_dir>")


if __name__ == "__main__":
    main()
