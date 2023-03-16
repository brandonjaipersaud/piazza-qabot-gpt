

CLASSIFY_PROMPT = """

Task Description: Classify each question posted on an undergraduate course discussion board into one of the following 4 categories: conceptual", "homework", "logistics" or "not answerable.
A question that requires instructor intervention should be classified as "not answerable". Questions that point out contradictions in assignment instructions and deadlines 
should be classified as "not answerable". Conceptual questions should be classified as "conceptual". Homework and lab questions that provide enough information to 
be answered should be classified as "conceptual". Questions that need course content related context to be answered such as an assignment handout should be classified as "homework". Questions that need logistical context to be answered such as a course syllabus should be classified
as "logistics". 


Question: Is the A1 Q2 code for debugging a neural network correct? It says we should debug using a large dataset. However, using a small dataset seems to make more sense here.
Classification: homework

Question: A1 Q4. Is lambda > 0 a necessary condition for this question?
Classification: homework

Question: How do you export a Colab notebook?
Classification: conceptual

Question: Below is the implementation for the sigmoid function: y=x Is this comment code in lab 4 correct since the implementation looks like a linear function instead?"
Classification: conceptual

Question: How do you submit a file on Markus?
Classification: conceptual

Question: Where is Toronto?
Classification: conceptual

Question: I believe the TA incorrectly added up the points on my midterm. Can I get a regrade please?
Classification: not answerable

Question: HW 1 Q2b: Does it really have to be sketched by hand?
Classification: homework

Question: A4. Will we lose marks for doing x on the assignment?
Classification: homework

Question: When is the exam? Where is it being held?
Classification: logistics

Question: Where is DV128?
Classification: logistics

Question: Just to double-check, are we allowed to use np.argmax() in the lab?
Classification: not answerable

Question: Is writing our aid sheet on an ipad then printing that out okay for the midterm?
Classification: not answerable

Question: Lab5 Q2. Isn't that the equation for a value function?
Classification: homework

Question: The assignment says x. Is this a typo?
Classification: not answerable

Question: Below is the implementation for the sigmoid function Is this comment code in lab 4 correct since the below implementation looks like a linear function instead?"
Classification: homework

Question: What does $x$ and $y$ represent in A1 Q2?
Classification: homework

Question: I keep getting the following error. Any tips for how to debug this piece of code?
Classification: homework

Question: Lab 2. For Q2, do we need to square the softmax function for numerical stability?
Classification: homework

Question: What material is being covered on the exam?
Classification: logistics

Question: Lab 2 Q1. What does gradient descent mean?
Classification: conceptual

Question: What are some strategies for splitting the dataset into train, validation and test sets?
Classification: conceptual

Question: Lab 2 Q4. What does np.shape() do?
Classification: conceptual

Question: Why does a neural net with a single hidden unit produce a linear decision boundary?
Classification: conceptual

Question: The assignment says 1+1=2. However, in lecture we learned that 1+1=0. Which explanation should we go with?
Classification: not answerable

Question: How does gradient descent work?
Classification: conceptual

Question: Why are we allowed to square the Hamming Distance in Lab2? Is it because of its monotonicity?
Classification: homework

Question: Lab3. So for the pred function in part 2 of the lab, is this the correct way to do it?
Classification: homework

Question: How do we approach this question on the homework?
Edit: nvm, I just solved it.
Classification: not answerable

Question: lab5 backward. i get stuck on the function backward(). I get a graph like this. Any help?
Classification: homework

Question: Is the following code for building a 2-layer MLP in Pytorch correct?: def forward(self, x):
        x = self.a1(x)
        x = self.relu(x)
        x = self.a2(x)
        return x
Classification: conceptual

Question: {}
Classification:"""



ANSWER_PROMPT = """
Task: Answer the following question that was posted by a student on a course discussion board for an introductory machine learning course. 
Your answer should be truthful, concise and helpful to the student. 

Question:{0}

Answer:"""



LOGPROB_PROMPT = """
Task: Answer the following question that was posted by a student on a course discussion board for an introductory machine learning course. 
Your answer should be truthful, concise and helpful to the student. 

Question:{0}

Answer:{1}"""