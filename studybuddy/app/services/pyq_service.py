"""
PYQ Service - Previous Year Question Paper Analysis
"""
from typing import List, Dict
from collections import Counter
import re
from app.services.pinecone_vector_service import query_vector_store_pinecone
from app.services.llm_service import get_llm

# async def extract_questions_from_pyq(pyq_text: str) -> List[Dict]:
#     """
#     Extract individual questions from PYQ text
    
#     Args:
#         pyq_text: Full text from PYQ PDF
        
#     Returns:
#         List of questions with metadata
#     """
#     # Simple pattern matching for questions
#     # Patterns: "Q1.", "1)", "Question 1:", etc.
#     question_patterns = [
#         r'Q\.?\s*\d+[\.:)]',  # Q1. or Q.1:
#         r'\d+[\.:)]\s+',       # 1. or 1:
#         r'Question\s+\d+',     # Question 1
#     ]
    
#     questions=[]
#     lines= pyq_text.split('\n')
#     current_question = ""
#     question_number = 0
    
#     for line in lines:
#         line= line.strip()
#         if not line:
#             continue
#         is_question_start=any(re.match(pattern, line) for pattern in question_patterns)
        
#         if is_question_start:
#             if current_question:
#                 question_number += 1
#                 questions.append({
#                     "question_number": question_number,
#                     "text": current_question.strip(),
#                     "word_count": len(current_question.split())
#                 })
#             current_question = line
#         else:
#             current_question += " " + line
            
#     if current_question:
#         question_number+=1
#         questions.append({
#             "question_number": question_number,
#             "text": current_question.strip(),
#             "word_count": len(current_question.split())
#         })
    
#     return questions

async def extract_questions_from_pyq(pyq_text: str) -> List[Dict]:
    """
    Extract questions using LLM - most reliable method
    """
    from app.services.llm_service import get_llm
    
    # Clean text
    pyq_text = re.sub(r'---\s*Page\s+\d+\s*---', '', pyq_text)
    
    # Use LLM to extract questions
    llm = get_llm()
    
    prompt = f"""Extract all individual questions from this exam paper. Return ONLY a JSON array of questions.

EXAM PAPER TEXT:
{pyq_text[:3000]}  # Limit to avoid token limits

Format:
[
  {{"number": 1, "text": "Define Machine Learning and explain its types."}},
  {{"number": 2, "text": "What is the difference between overfitting and underfitting?"}},
  ...
]

Return ONLY the JSON array, nothing else."""

    try:
        response = llm.invoke(prompt)
        response_text = response.content.strip()
        
        # Remove markdown code blocks if present
        response_text = re.sub(r'```json\s*|\s*```', '', response_text)
        
        # Parse JSON
        import json
        questions_data = json.loads(response_text)
        
        # Convert to our format
        questions = [
            {
                "question_number": q.get("number", i+1),
                "text": q.get("text", ""),
                "word_count": len(q.get("text", "").split())
            }
            for i, q in enumerate(questions_data)
            if q.get("text")  # Only include if has text
        ]
        
        return questions
        
    except Exception as e:
        print(f"LLM extraction failed: {e}")
        # Fallback to simple extraction
        return []
    
async def map_questions_to_topics(
    questions: List[Dict],
    syllabus_file_id: str
) -> List[Dict]:
    """
    Map each question to syllabus topics using semantic search
    
    Args:
        questions: List of questions from PYQ
        syllabus_file_id: File ID of syllabus
        
    Returns:
        Questions with mapped topics
    """
    mapped_questions = []
    
    for question in questions:
        relevant_chunks = await query_vector_store_pinecone(
            file_id=syllabus_file_id,
            question=question["text"],
            k=2  
        )
    
        topics = []
        for chunk in relevant_chunks:
            content = chunk["content"][:200]  
            topics.append({
                "content": content,
                "similarity": chunk["similarity_score"]
            })
        
        mapped_questions.append({
            **question,
            "mapped_topics": topics,
            "primary_topic": topics[0]["content"][:50] if topics else "Unknown"
        })
    
    return mapped_questions

async def analyze_topic_frequency(mapped_questions: List[Dict]) -> Dict:
    """
    Analyze which topics appear most frequently in PYQs
    
    Args:
        mapped_questions: Questions with mapped topics
        
    Returns:
        Topic frequency analysis
    """
    topic_counter = Counter()
    
    for question in mapped_questions:
        primary_topic = question.get("primary_topic", "Unknown")
        topic_counter[primary_topic] += 1
        
    total_questions = len(mapped_questions)
    topic_analysis = {}
    
    for topic, count in topic_counter.most_common():
        percentage = (count / total_questions) * 100
        topic_analysis[topic] = {
            "count": count,
            "percentage": round(percentage, 2),
            "priority": "HIGH" if percentage > 20 else "MEDIUM" if percentage > 10 else "LOW"
        }
    return topic_analysis

async def generate_study_recommendations(
    topic_analysis: Dict,
    mapped_questions: List[Dict]
) -> Dict:
    """
    Generate smart study recommendations based on PYQ analysis
    
    Args:
        topic_analysis: Frequency analysis
        mapped_questions: Questions with topics
        
    Returns:
        Study recommendations
    """
    recommendations=[]
    priorty_topics=[]
    
    for topic, data in topic_analysis.items():
        if data["priority"] == "HIGH":
            priorty_topics.append(topic)
            recommendations.append(
                f"🔥 PRIORITY: Focus on '{topic}' - appears in {data['count']} questions ({data['percentage']}%)"
            )
            
    for topic, data in topic_analysis.items():
        if data["priority"] == "MEDIUM":
            recommendations.append(
                f"⚠️ Important: Review '{topic}' - {data['count']} questions ({data['percentage']}%)"
            )
            
    avg_word_count = sum(q["word_count"] for q in mapped_questions) / len(mapped_questions)
    recommendations.append(
        f"📝 Average question length: {int(avg_word_count)} words - prepare accordingly"
    )
    
    return {
        "recommendations": recommendations,
        "priority_topics": priorty_topics,
        "total_questions_analyzed": len(mapped_questions),
        "unique_topics": len(topic_analysis)
    }
    
async def generate_mock_questions(
    syllabus_file_id: str,
    topic: str,
    num_questions: int = 5
) -> List[Dict]:
    """
    Generate mock questions based on syllabus topics
    
    Args:
        syllabus_file_id: File ID of syllabus
        topic: Topic to generate questions about
        num_questions: Number of questions to generate
        
    Returns:
        List of generated questions
    """
    llm=get_llm()
    
    relevant_chunks = await query_vector_store_pinecone(
        file_id=syllabus_file_id,
        question=topic,
        k=2
    )
    context = "\n".join([chunk["content"][:300] for chunk in relevant_chunks])
    
    prompt = f"""You are an exam question generator. Based on the syllabus content below, generate {num_questions} exam-style questions about "{topic}".

SYLLABUS CONTENT:
{context}

Generate questions that:
1. Test understanding of key concepts
2. Are clear and unambiguous
3. Match typical exam difficulty
4. Cover different aspects of the topic

Format each question as:
Q1: [Question text]
Q2: [Question text]
...

GENERATE {num_questions} QUESTIONS:"""
    
    response = llm.invoke(prompt)
    questions_text = response.content
    
    # Parse generated questions
    questions = []
    for i, line in enumerate(questions_text.split('\n'), 1):
        line = line.strip()
        if line and (line.startswith('Q') or line.startswith(str(i))):
            question_text = re.sub(r'^Q\.?\s*\d+[\.:)]\s*', '', line)
            question_text = re.sub(r'^\d+[\.:)]\s*', '', question_text)
            
            if question_text:
                questions.append({
                    "question_number": i,
                    "text": question_text,
                    "topic": topic,
                    "difficulty": "medium"
                })
    
    return questions[:num_questions]