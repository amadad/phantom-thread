Extract the stylistic essence of a given text and generate a prompt to replicate its style. Follow the structured steps below to achieve this - pay close attention to header/subsection styles, and the way the source writing starts and ends stylistically.
### Step 1: Contextual Insight Gathering
- **Identify the Target Audience**: Determine who the text is intended for and how this influences the style.
- **Determine the Primary Purpose**: Understand if the text is meant to inform, persuade, entertain, etc.
- **Classify the Genre**: Identify the genre and note standard stylistic conventions.
- **Output**: A contextual framework that informs the replication process.
### Step 2: Essence Extraction
- **Comprehensive Review**: Mark key stylistic features throughout the text.
- **Use Text Analysis Tools**: Utilize tools for deeper insights into stylistic elements.
- **Output**: An inventory of key stylistic elements.
### Step 3: Stylistic Decomposition
- **Catalog Sentence Structures**: Note the types of sentences used (simple, compound, complex) and their lengths.
- **Lexicon Analysis**: Examine the vocabulary for technical terms, everyday language, or jargon.
- **Pacing and Rhythm**: Observe the flow and pacing of the text.
- **Motifs and Themes**: Identify recurring motifs or themes.
- **Output**: A detailed breakdown of style components.
### Step 4: Linguistic Nuance Identification
- **Idiomatic Expressions**: Identify any idioms, jargon, or colloquialisms.
- **Metaphorical Language**: Note the use of metaphors, similes, and other figurative language.
- **Rhetorical Strategies**: Examine the use of rhetorical devices.
- **Output**: Understanding of linguistic nuances.
### Step 5: Tonal Mapping
- **Emotional Resonance**: Assess the emotional tone of the text using sentiment analysis tools.
- **Formality Level**: Determine the level of formality.
- **Output**: A comprehensive tone profile.
### Step 6: Structural Blueprinting
- **Idea Arrangement**: Analyze how ideas are organized and presented.
- **Visual Mapping**: Create visual maps of the text's structure.
- **Output**: A structural design blueprint.
### Step 7: Directive Synthesis
- **Actionable Directives**: Translate the analysis into actionable steps for replication.
- **Style Replication Template**: Develop a template for replicating the style.
- **Output**: Actionable style replication guidelines.
### Step 8: Exemplar Generation
- **Produce Text Samples**: Create sample texts that demonstrate the analyzed style.
- **Draft Paragraphs**: Write paragraphs following the synthesized directives. **Specify whether the text should include bullets, lists, bullet points, or numbered steps, or if it should be in long-form paragraph format.**
- **Variability Testing**: Test the style with different contexts.
- **Output**: Text exemplars in the original style.
### Step 9: Comparative Evaluation
- **Fidelity Check**: Ensure the new text matches the source style.
- **Side-by-Side Comparison**: Conduct blind reviews to compare the texts.
- **Discrepancy Resolution**: Address any identified discrepancies.
- **Output**: A refined replication strategy.
### Step 10: Prompt Creation
- **Role Assignment**: Act as a prompt engineer and generate a prompt that injects all the style extracted from the document as a part of the prompt.
- **Style Integration**: Ensure that the prompt includes the stylistic elements identified in previous steps.
- **Topic Placement**: Place a variable called `{{Topic}}` at the bottom of the prompt and reference it within the prompt.
- **Output**: A comprehensive prompt outputted in markdown that replicates the original style while allowing for topic customization. Include 3 to 5 exact extraction samples from the source document as examples to enhance the multishot prompt.
### Example Prompt:
```markdown
You are an expert in writing motivational and informative articles on personal development. Your task is to write a comprehensive article about `{{Topic}}`, following the structured and engaging style outlined below. **Ensure that the text adheres strictly to long-form paragraph format without any lists, bullets, or numbered steps if specified. If lists, bullets, or numbered steps are included in the style, integrate them appropriately.**
**Introduction**:
- Begin with a rhetorical question to engage the reader and introduce the topic.
- Follow with a concise thesis statement that outlines the main idea of the article.
**Definition and Explanation**:
- Provide clear definitions and explanations of key concepts related to the topic.
- Use examples and analogies to make complex ideas more accessible.
**Components Breakdown**:
- Discuss the various elements that make up the main concept in detail.
- Provide sub-sections within this part if necessary to cover each element thoroughly.
**Importance and Benefits**:
- Explain why the concept is important and what benefits it brings.
- Include real-life examples and evidence to support your points.
**Practical Strategies**:
- Offer practical advice and strategies for implementing the concept in daily life.
- Use hypothetical scenarios to illustrate how these strategies can be applied.
**Challenges and Solutions**:
- Address potential obstacles and provide solutions to overcome them.
- Discuss common pitfalls and how to avoid them, supported by anecdotal evidence.
**Conclusion**:
- End with an encouraging and motivational message that reinforces the main points.
- Suggest a call to action or a thought-provoking question to leave a lasting impact.
### Example Sections:
**Introduction**:
So, what's the deal with discipline?
Discipline is often touted as the secret ingredient to success, but what exactly is it, and why does it matter so much? At its core, discipline is the ability to control one's behavior, thoughts, and actions in pursuit of a specific goal. It's about consistency and perseverance, showing up day after day, even when motivation is low or circumstances are challenging.
**Components Breakdown**:
What makes up this thing called discipline?
Discipline isn't just one single thing - it's a combination of several key elements working together. First, there's self-control, which is the ability to regulate one's emotions, impulses, and behaviors. This goes hand in hand with goal-setting, as clearly defining what you want to achieve and why is crucial for maintaining discipline.
**Importance and Benefits**:
Why should we care about discipline anyway?
The importance of discipline cannot be overstated, as it plays a crucial role in various aspects of life. In terms of personal development, discipline enables individuals to work consistently towards self-improvement, whether it's learning new skills, breaking bad habits, or developing positive ones.
Follow this structure and tone to create an article that is both informative and motivating, ensuring that all advice is practical and supported with relatable examples.
{{Topic}} = ''
