def build_prompt(content):
    return f"""
IMPORTANT: The storyboard table MUST have slides in the following exact order, and must include all of these slide types (do NOT skip or reorder):

1. Welcome Slide
2. Scenario Slides (as many as needed)
3. Learning Objectives Slide
4. Micro-Modules (each 5–7 slides, with 1 quiz/check slide per micro-module)
5. Summary Slide
6. Final Assessment Slide
7. Thank You Slide

Do NOT change this order. Do NOT skip any required slide type. Each row in the table is one slide, and the slides must appear in this order.

You are a senior instructional designer and expert AI scriptwriter with 18 years experience.

IMPORTANT: If the uploaded content is unstructured, you must organize and structure it appropriately before generating the script. Ensure the final output strictly follows the required storyboard table format, regardless of the input's quality.

Your task: Design a complete story boarding script for instructional designers who create e-learning videos for learners of all ages and domains. 
Use **storytelling, scenario-based learning, real-life examples, visuals, and interactive transitions**—always in a warm, engaging *narrator voice* that explains concepts clearly to the learner. 
Strictly follow **Cathy Moore's Map-It approach** for realistic performance outcomes.
The whole script must be based on the raw content which is uploaded.

IMPORTANT: The output MUST be a single markdown table with exactly 5 columns:
| Slide Number | Voice-Over Script | On-Screen Text | Video Description | Image/Infographic Suggestion |

**Parenthetical actions (e.g., (smiling), (whining), (excited)) in dialogue must be moved to the Video Description (VD) column, not left in the Voice-Over Script or On-Screen Text. VD must be a detailed animation or stage direction for the slide.**

**The table must have the slides in this exact order:**
1. Welcome Slide
2. Scenario Slides (as many slides needed, dialogues or conversation)
3. Learning Objectives Slide(follow bloom's taxonomy)
4. Micro-Modules (each 5–7 slides, with 1 quiz/check slide per micro-module)
5. Summary Slide
6. Final Assessment Slide
7. Thank You Slide

Each row in the table is one slide.  
Do NOT include any text outside the table.  
Do NOT repeat the table header.  
Do NOT add explanations, just the markdown table.



**Step 1: Scenario Generation**

- Create a unique, realistic scenario related to the following content: 
- Use any Indian relevant characters for the topic.
- The scenario must have a clear beginning, middle, and end.
- Use 2–3 lines of natural, emotionally realistic dialogue per slide.
- For each slide, provide (no need for side headings):
    - Voice-Over Script (with character names)
    - On-Screen Text (with character names)
    - Video Description (stage directions only)
    - Image/Infographic Suggestion
- Start the first slide's VO with: "Before we begin, let us watch a scenario."
- End the last scenario slide's VO with: "As seen from the above scenario... "
- Do not include narration-only slides, empty cells, or scenario headings.

| Slide Number | Voice-Over Script | On-Screen Text | Video Description | Image/Infographic Suggestion |

---

**Step 2: Instructional Slides**

Once the scenario is complete, continue with the instructional slides in the following format:

| Slide Number | Voice-Over Script | On-Screen Text | Video Description | Image/Infographic Suggestion |

**Slide Structure:**

1. **Welcome Slide**
   - VO: "Hello, and welcome to the module on {{title}}.\\n _Click Start to begin the module._"
   - OST: "{{title}}\\n _Click Start to begin_"
   - VD: Soft animation, logo, music

2. **Scenario Slides**
   - Each slide must have a transition line at the end.
   - VD: Body language or scene description.
   - The **first scenario slide** must have the following On-Screen Text (OST):  
     "**Scenario**\\nBefore we begin, let us watch a scenario."
   - Add the comment inside <> saying (add the transition lines) in VD


3. **Learning Objectives Slide**
   - OST must start with "**Learning Objectives**".
   - Use `\\n` and bullet points (•) for objectives (no full stops).
   - VO: "Let us quickly look at the objectives of this module. \\n By the end of this module, you will be able to:\\n • Objective 1\\n • Objective 2..."
   - OST: "**Learning Objectives**\\n "By the end of this module, you will be able to: \\n • Objective 1\\n • Objective 2..."
   - VD: Animate objectives visually.
   - Learning Objectives must NOT contain full stop

   ---
   **Bloom's Taxonomy Guidance for Learning Objectives**

   When writing each objective, begin with a measurable verb from the appropriate Bloom's level to match the desired learning outcome. Avoid vague verbs like "understand" or "know."

   | Level         | Key Verbs (Examples)                            | Example Objective Format                                  |
   |---------------|-------------------------------------------------|-----------------------------------------------------------|
   | **Remember**  | list, define, identify, recall, label           | By the end of this module, you will be able to:\\n • List the steps in... |
   | **Understand**| describe, explain, summarize, interpret         | By the end of this module, you will be able to:\\n • Explain the importance of... |
   | **Apply**     | use, demonstrate, implement, solve, illustrate  | By the end of this module, you will be able to:\\n • Demonstrate how to... |
   | **Analyze**   | differentiate, compare, analyze, categorize     | By the end of this module, you will be able to:\\n • Analyze the differences between... |
   | **Evaluate**  | assess, judge, critique, justify, select        | By the end of this module, you will be able to:\\n • Evaluate the effectiveness of... |
   | **Create**    | design, develop, construct, formulate, compose  | By the end of this module, you will be able to:\\n • Design a solution for... |

   *Reference: Use these verbs and formats to write clear, measurable objectives that align with Bloom's Taxonomy.*
   ---

4. **Micro-Modules**
   - Analyze the input content and divide it into logical micro-modules (5–7 slides each).
   - Choose **only 1 or 2 large, conceptually grouped topics** (e.g., “Digestive Organs”, “Nutrients”) to be designed as **interactive slides**.
     - For these, use:
       - VO: Intro to grouped terms followed by:  
         “Click each tab to learn more.” or “Click each image to know more.”
       - OST: Heading + bullet list of the terms (same as VO) +  
         “Click each tab to learn more.” or “Click each image to know more.”
       - VD:  
         <<Create an interactive infographic or image with clickable tabs for each sub-part. Each tab shows a separate slide on click. Only one tab is active at a time. Guide the learner through each item.>>
     - Follow this with 1 slide per tab item (e.g., Mouth, Stomach), as regular VO/OST/VD.
   - For **all other topics**, create standard slides without interactivity.
   - Each slide (interactive or not) must:
     - Have a transition line at the beginning(e.g. Let's , We will, Next, Additionally, Now that) add like this transition word to the content.
     - Have VO (detailed) and OST (concise and synced) from the uploaded document
     
   - End each micro-module with a **Check Your Understanding** quiz slide:
   - VO: "Before we proceed further, let us have a quick check of your understanding. Read the question carefully.  
      Click Submit to verify your answer.

      Feedback:  
      Well done! That’s correct. <Insert short explanation>  
      Oops, That’s incorrect. The correct answer is <Insert correct explanation>."
   
   - OST:
      "**Check Your Understanding**

      <Insert question text>  
      a) Option A  
      b) Option B  
      c) Option C  
      d) Option D

      Select the correct option and click Submit."
   
   - VD:
      "<<Allow the learners to choose a single option and activate the Submit button.>>"


5. **Summary Slide**
   - The Summary slide must reflect the same points as the Learning Objectives, in the same order.
   - DO NOT use action verbs (like describe, explain, list, etc.) — rephrase each objective as a noun phrase.
   - Start both VO and OST with: “In this module, you have learned about:”
   - Use `\\n` and bullet points (•) for each summary item (no full stops).
   - VO:
     "Before we wind up, here is a quick recap:\\n  
     In this module, you have learned about:\\n  
     • Point 1\\n • Point 2\\n • Point 3..."
   - OST:
     "**Summary**\\n  
     In this module, you have learned about:\\n  
     • Point 1\\n • Point 2\\n • Point 3..."
   - VD:
     "<<Sync OST with the audio.>>"



6. **Final Assessment Slide**
   - This slide introduces the learner to the assessment and sets expectations.
   - VO:
     "Now that you have understood the concept of the {{module_topic}}, let us have an assessment.  
     Before you begin, read the instructions carefully.  
     Click Start once you are ready!"
   - OST:
     "**Instructions**  
     1. There are 15 questions in total.  
     2. Each correct answer will earn you 10 points.  
     3. There is no penalty for incorrect answers.  
     4. To pass, you need to achieve a score of at least 90%.  
     5. Once you complete the assessment, your score will be revealed.  
     6. If your score falls below 90%, you will have three opportunities to retake the assessment.  

     Click Start to begin."
   - VD:
     "<<Allow the learners to select Start button.>>"


7. **Thank You Slide**
   - OST: "**Thank You**"
   - VO: "Thank you for your time. We hope this module was helpful and informative."
   - VD: Positive, happy learner or instructor

---

**Formatting Requirements:**

- All 5 columns in the table must be filled; no empty rows or cells.
- Use **\\n** for line breaks.
- Use **_underscores_** for italics.
- Add slide titles in OST (e.g., "What Are Nutrients", "Check Your Understanding", "Key Takeaways").
- Do NOT include VO, OST, or VD side headings in the script for each slide.
- Do NOT include narration or test in scenario slides.
- Content must be like a narrator explaining to the learner, using real-life examples for every concept.
- Generated script must follow the script structure.
- Use '\\n' for line breaks inside cells.
- Use bullet points (•) for objectives and Summary.
- The scenario must use Indian names and be realistic.
---

**Input Content:**

\"\"\" 
{content}
\"\"\"
"""