import json
import os
import hashlib
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from advanced_plugin_manager import BasePlugin
import requests
from bs4 import BeautifulSoup

class KnowledgeBasePlugin(BasePlugin):
    """
    Advanced Knowledge Base Plugin for Self-Learning AI Assistant
    
    Features:
    - Store and retrieve learned information
    - Auto-learn from web searches
    - Context-aware knowledge matching
    - Knowledge expiration and updates
    - Confidence scoring
    """
    
    def __init__(self):
        super().__init__()
        self.description = "Store, retrieve, and learn knowledge automatically"
        self.commands = ["learn", "remember", "recall", "forget", "knowledge", "teach", "what is", "who is", "explain"]
        
        # Knowledge storage
        self.knowledge_file = "knowledge_base.json"
        self.knowledge_base = self.load_knowledge_base()
        
        # Learning settings
        self.auto_learn = True
        self.confidence_threshold = 0.7
        self.max_knowledge_age_days = 30
        
    def load_knowledge_base(self) -> Dict[str, Any]:
        """Load the knowledge base from file"""
        if os.path.exists(self.knowledge_file):
            try:
                with open(self.knowledge_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading knowledge base: {e}")
                return {"entries": {}, "topics": {}, "metadata": {"created": datetime.now().isoformat()}}
        return {"entries": {}, "topics": {}, "metadata": {"created": datetime.now().isoformat()}}
    
    def save_knowledge_base(self):
        """Save the knowledge base to file"""
        try:
            with open(self.knowledge_file, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge_base, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving knowledge base: {e}")
    
    def handle_command(self, command: str, **kwargs) -> str:
        """Handle knowledge base commands"""
        command_lower = command.lower().strip()
        
        # Direct knowledge commands
        if command_lower.startswith(("what is", "who is", "what are", "who are")):
            return self.answer_question(command)
        elif command_lower.startswith("explain"):
            return self.explain_topic(command)
        elif command_lower.startswith("learn"):
            return self.manual_learn(command)
        elif command_lower.startswith("remember"):
            return self.remember_information(command)
        elif command_lower.startswith("forget"):
            return self.forget_information(command)
        elif "knowledge" in command_lower:
            if "show" in command_lower or "list" in command_lower:
                return self.list_knowledge()
            elif "clear" in command_lower:
                return self.clear_knowledge()
        
        # Try to find relevant knowledge for any query
        return self.search_knowledge(command)
    
    def answer_question(self, question: str) -> str:
        """Answer a 'what is' or 'who is' question"""
        # Extract the topic from the question
        question_lower = question.lower()
        
        # Remove question words to get the topic
        for starter in ["what is", "who is", "what are", "who are", "what's", "who's"]:
            if question_lower.startswith(starter):
                topic = question[len(starter):].strip()
                break
        else:
            topic = question.strip()
        
        # Remove articles and common words
        topic = re.sub(r'\b(a|an|the)\b', '', topic, flags=re.IGNORECASE).strip()
        
        # Search existing knowledge
        result = self.search_knowledge(topic)
        
        if result and "I don't have information" not in result:
            return result
        
        # If no knowledge found, try to learn it
        if self.auto_learn:
            return self.auto_learn_topic(topic, question)
        else:
            return f"I don't have information about '{topic}'. Would you like me to search for it?"
    
    def explain_topic(self, command: str) -> str:
        """Explain a topic in detail"""
        topic = command.replace("explain", "").strip()
        
        # Search for detailed explanation
        result = self.search_knowledge(topic, detailed=True)
        
        if result and "I don't have information" not in result:
            return f"📚 Explanation of {topic}:\n\n{result}"
        
        # Auto-learn if enabled
        if self.auto_learn:
            return self.auto_learn_topic(topic, f"explain {topic}", detailed=True)
        else:
            return f"I don't have detailed information about '{topic}'. Would you like me to search for it?"
    
    def auto_learn_topic(self, topic: str, original_question: str, detailed: bool = False) -> str:
        """Automatically learn about a topic from web search"""
        try:
            print(f"🧠 Learning about: {topic}")
            
            # Search for information
            search_results = self.web_search_and_extract(topic, detailed)
            
            if search_results:
                # Store the learned information
                self.store_knowledge(topic, search_results, source="web_search", confidence=0.8)
                
                # Return the learned information
                return f"🧠 I learned about {topic}:\n\n{search_results['summary']}"
            else:
                return f"❌ I couldn't find reliable information about '{topic}' to learn from."
                
        except Exception as e:
            return f"❌ Error while learning about '{topic}': {str(e)}"
    
    def web_search_and_extract(self, topic: str, detailed: bool = False) -> Optional[Dict[str, Any]]:
        """Search the web and extract knowledge about a topic"""
        try:
            # Use multiple sources for better information
            sources = []
            
            # Try Wikipedia first (most reliable)
            wiki_info = self.search_wikipedia(topic)
            if wiki_info:
                sources.append({"source": "wikipedia", "content": wiki_info, "reliability": 0.9})
            
            # Try Google search
            google_info = self.search_google_extract(topic, detailed)
            if google_info:
                sources.append({"source": "google", "content": google_info, "reliability": 0.7})
            
            if not sources:
                return None
            
            # Combine and process information
            combined_info = self.process_search_results(sources, topic, detailed)
            return combined_info
            
        except Exception as e:
            print(f"Error in web search: {e}")
            return None
    
    def search_wikipedia(self, topic: str) -> Optional[str]:
        """Search Wikipedia for topic information"""
        try:
            import wikipedia
            
            # Search for the topic
            search_results = wikipedia.search(topic, results=3)
            
            if search_results:
                # Get the first result
                page = wikipedia.page(search_results[0])
                
                # Get summary (first few sentences)
                summary = wikipedia.summary(search_results[0], sentences=3)
                
                return {
                    "title": page.title,
                    "summary": summary,
                    "url": page.url,
                    "full_content": page.content[:2000]  # First 2000 chars
                }
        except Exception as e:
            print(f"Wikipedia search error: {e}")
            return None
    
    def search_google_extract(self, topic: str, detailed: bool = False) -> Optional[str]:
        """Search Google and extract information"""
        try:
            # Create search query
            query = f"{topic} definition explanation"
            
            # Use a simple web scraping approach
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            response = requests.get(search_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for featured snippets or knowledge panels
                snippets = []
                
                # Try to find featured snippet
                featured = soup.find('div', {'class': ['featured-snippet', 'kno-rdesc']})
                if featured:
                    snippets.append(featured.get_text().strip())
                
                # Look for other relevant content
                for elem in soup.find_all(['p', 'div'], limit=5):
                    text = elem.get_text().strip()
                    if len(text) > 50 and topic.lower() in text.lower():
                        snippets.append(text)
                
                if snippets:
                    return {
                        "summary": snippets[0][:500],  # First snippet, truncated
                        "additional": snippets[1:3] if len(snippets) > 1 else []
                    }
            
            return None
            
        except Exception as e:
            print(f"Google search error: {e}")
            return None
    
    def process_search_results(self, sources: List[Dict], topic: str, detailed: bool) -> Dict[str, Any]:
        """Process and combine search results into knowledge"""
        try:
            # Start with the most reliable source
            sources.sort(key=lambda x: x['reliability'], reverse=True)
            
            primary_source = sources[0]
            content = primary_source['content']
            
            if isinstance(content, dict):
                summary = content.get('summary', '')
                title = content.get('title', topic)
                additional_info = content.get('additional', [])
            else:
                summary = str(content)[:500]
                title = topic
                additional_info = []
            
            # Create knowledge entry
            knowledge_entry = {
                "topic": title,
                "summary": summary,
                "details": additional_info if detailed else [],
                "sources": [s['source'] for s in sources],
                "confidence": max(s['reliability'] for s in sources),
                "learned_date": datetime.now().isoformat(),
                "query_count": 0
            }
            
            return knowledge_entry
            
        except Exception as e:
            print(f"Error processing search results: {e}")
            return None
    
    def store_knowledge(self, topic: str, knowledge: Dict[str, Any], source: str = "manual", confidence: float = 1.0):
        """Store knowledge in the knowledge base"""
        try:
            # Create a normalized key for the topic
            topic_key = self.normalize_topic(topic)
            
            # Add metadata
            knowledge.update({
                "source": source,
                "confidence": confidence,
                "stored_date": datetime.now().isoformat(),
                "last_accessed": datetime.now().isoformat(),
                "access_count": 0
            })
            
            # Store in knowledge base
            self.knowledge_base["entries"][topic_key] = knowledge
            
            # Update topic index
            self.update_topic_index(topic, topic_key)
            
            # Save to file
            self.save_knowledge_base()
            
            print(f"📚 Stored knowledge about: {topic}")
            
        except Exception as e:
            print(f"Error storing knowledge: {e}")
    
    def search_knowledge(self, query: str, detailed: bool = False) -> str:
        """Search the knowledge base for relevant information"""
        try:
            query_lower = query.lower()
            best_match = None
            best_score = 0
            
            # Search through stored knowledge
            for topic_key, knowledge in self.knowledge_base["entries"].items():
                # Calculate relevance score
                score = self.calculate_relevance(query_lower, topic_key, knowledge)
                
                if score > best_score and score > self.confidence_threshold:
                    best_score = score
                    best_match = knowledge
            
            if best_match:
                # Update access statistics
                best_match["access_count"] = best_match.get("access_count", 0) + 1
                best_match["last_accessed"] = datetime.now().isoformat()
                self.save_knowledge_base()
                
                # Format response
                response = best_match.get("summary", "")
                
                if detailed and best_match.get("details"):
                    response += "\n\n" + "\n".join(best_match["details"][:3])
                
                # Add confidence indicator
                confidence = best_match.get("confidence", 0)
                if confidence < 0.8:
                    response += f"\n\n(Confidence: {confidence:.1%})"
                
                return response
            
            return f"I don't have information about '{query}' in my knowledge base."
            
        except Exception as e:
            return f"Error searching knowledge: {e}"
    
    def calculate_relevance(self, query: str, topic_key: str, knowledge: Dict) -> float:
        """Calculate how relevant a knowledge entry is to a query"""
        score = 0.0
        
        # Check topic key match
        if query in topic_key.lower():
            score += 0.8
        
        # Check summary match
        summary = knowledge.get("summary", "").lower()
        query_words = query.split()
        
        for word in query_words:
            if len(word) > 2:  # Skip short words
                if word in summary:
                    score += 0.2
                if word in topic_key:
                    score += 0.3
        
        # Boost score for exact topic matches
        topic = knowledge.get("topic", "").lower()
        if query in topic or topic in query:
            score += 0.5
        
        # Apply confidence factor
        confidence = knowledge.get("confidence", 0.5)
        score *= confidence
        
        return min(score, 1.0)
    
    def normalize_topic(self, topic: str) -> str:
        """Normalize a topic for consistent storage"""
        # Convert to lowercase, remove extra spaces and special chars
        normalized = re.sub(r'[^\w\s]', '', topic.lower())
        normalized = re.sub(r'\s+', '_', normalized.strip())
        return normalized
    
    def update_topic_index(self, original_topic: str, topic_key: str):
        """Update the topic index for faster searching"""
        if "topics" not in self.knowledge_base:
            self.knowledge_base["topics"] = {}
        
        # Store various forms of the topic
        forms = [
            original_topic.lower(),
            topic_key,
            original_topic.replace(" ", "_").lower()
        ]
        
        for form in forms:
            self.knowledge_base["topics"][form] = topic_key
    
    def manual_learn(self, command: str) -> str:
        """Manually learn information"""
        # Extract topic and information from command
        parts = command.replace("learn", "").strip().split(":", 1)
        
        if len(parts) == 2:
            topic = parts[0].strip()
            information = parts[1].strip()
            
            knowledge = {
                "topic": topic,
                "summary": information,
                "details": [],
                "sources": ["manual"],
                "confidence": 1.0
            }
            
            self.store_knowledge(topic, knowledge, source="manual")
            return f"✅ I've learned that {topic}: {information}"
        else:
            return "Please use format: 'learn [topic]: [information]'"
    
    def remember_information(self, command: str) -> str:
        """Remember specific information"""
        info = command.replace("remember", "").strip()
        
        # Try to extract topic from the information
        topic = info.split()[0] if info.split() else "general_info"
        
        knowledge = {
            "topic": topic,
            "summary": info,
            "details": [],
            "sources": ["remember"],
            "confidence": 1.0
        }
        
        self.store_knowledge(topic, knowledge, source="remember")
        return f"✅ I'll remember: {info}"
    
    def forget_information(self, command: str) -> str:
        """Forget specific information"""
        topic = command.replace("forget", "").strip()
        topic_key = self.normalize_topic(topic)
        
        if topic_key in self.knowledge_base["entries"]:
            del self.knowledge_base["entries"][topic_key]
            self.save_knowledge_base()
            return f"✅ I've forgotten information about '{topic}'"
        else:
            return f"I don't have information about '{topic}' to forget."
    
    def list_knowledge(self) -> str:
        """List stored knowledge"""
        entries = self.knowledge_base.get("entries", {})
        
        if not entries:
            return "📚 My knowledge base is empty."
        
        knowledge_list = []
        for topic_key, knowledge in entries.items():
            topic = knowledge.get("topic", topic_key.replace("_", " "))
            confidence = knowledge.get("confidence", 0)
            access_count = knowledge.get("access_count", 0)
            
            knowledge_list.append(f"• {topic} (confidence: {confidence:.1%}, accessed: {access_count}x)")
        
        return f"📚 My Knowledge Base ({len(entries)} entries):\n\n" + "\n".join(knowledge_list[:20])
    
    def clear_knowledge(self) -> str:
        """Clear the knowledge base"""
        self.knowledge_base = {"entries": {}, "topics": {}, "metadata": {"created": datetime.now().isoformat()}}
        self.save_knowledge_base()
        return "🗑️ Knowledge base cleared."
    
    def cleanup_old_knowledge(self):
        """Remove old or low-confidence knowledge"""
        current_time = datetime.now()
        entries_to_remove = []
        
        for topic_key, knowledge in self.knowledge_base["entries"].items():
            # Check age
            stored_date = datetime.fromisoformat(knowledge.get("stored_date", current_time.isoformat()))
            age_days = (current_time - stored_date).days
            
            # Check confidence and usage
            confidence = knowledge.get("confidence", 0)
            access_count = knowledge.get("access_count", 0)
            
            # Remove if old and unused or low confidence
            if (age_days > self.max_knowledge_age_days and access_count == 0) or confidence < 0.3:
                entries_to_remove.append(topic_key)
        
        # Remove marked entries
        for topic_key in entries_to_remove:
            del self.knowledge_base["entries"][topic_key]
        
        if entries_to_remove:
            self.save_knowledge_base()
            print(f"🧹 Cleaned up {len(entries_to_remove)} old knowledge entries")
