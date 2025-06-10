"""
Enhanced Self-Learning Assistant Integration

This module enhances the main assistant with intelligent self-learning capabilities
"""

import re
from typing import Dict, Any, Optional, List

class LearningAssistantMixin:
    """
    Mixin class to add self-learning capabilities to the Smart Assistant
    """
    
    def __init__(self):
        # Learning settings
        self.learning_enabled = True
        self.auto_learn_threshold = 0.7  # Confidence threshold for auto-learning
        self.knowledge_cache = {}  # In-memory cache for frequently accessed knowledge
        
        # Learning triggers - phrases that indicate the user wants information
        self.learning_triggers = [
            "what is", "who is", "what are", "who are", "tell me about",
            "explain", "define", "definition of", "meaning of", 
            "i don't know", "i need to know", "can you tell me",
            "do you know", "have you heard of"
        ]
        
        # Unknown response patterns that trigger learning
        self.unknown_patterns = [
            "i don't know", "i'm not sure", "i don't have information",
            "i can't help with that", "i don't understand",
            "no information available", "not found"
        ]
    
    def enhanced_process_command(self, user_input: str) -> str:
        """
        Enhanced command processing with intelligent learning capabilities
        """
        print("🧠 Processing with learning...")
        
        # Check if this is a learning-worthy query
        if self.should_attempt_learning(user_input):
            # Try to get knowledge from knowledge base first
            kb_result = self.check_knowledge_base(user_input)
            if kb_result:
                print("📚 Found in knowledge base")
                return kb_result
        
        # Process with standard AI/plugin system
        standard_result = self.process_command_standard(user_input)
        
        # Check if the result indicates lack of knowledge
        if self.indicates_unknown(standard_result) and self.should_attempt_learning(user_input):
            print("🔍 Attempting to learn...")
            learned_result = self.attempt_auto_learning(user_input)
            if learned_result:
                return learned_result
        
        # Post-process to extract and store any new knowledge
        if self.learning_enabled:
            self.extract_and_store_knowledge(user_input, standard_result)
        
        return standard_result
    
    def should_attempt_learning(self, user_input: str) -> bool:
        """Check if this input warrants attempting to learn"""
        user_lower = user_input.lower()
        
        # Check for learning trigger phrases
        for trigger in self.learning_triggers:
            if trigger in user_lower:
                return True
        
        # Check for question patterns
        question_patterns = [
            r"^(what|who|where|when|why|how)\s",
            r"\?\s*$",  # Ends with question mark
            r"^(can you|could you|do you know)"
        ]
        
        for pattern in question_patterns:
            if re.search(pattern, user_lower):
                return True
        
        return False
    
    def indicates_unknown(self, response: str) -> bool:
        """Check if a response indicates lack of knowledge"""
        response_lower = response.lower()
        
        for pattern in self.unknown_patterns:
            if pattern in response_lower:
                return True
        
        # Check for other indicators
        if len(response) < 50 and any(word in response_lower for word in ["sorry", "can't", "unable"]):
            return True
        
        return False
    
    def check_knowledge_base(self, query: str) -> Optional[str]:
        """Check if we have knowledge about this query"""
        try:
            # Get knowledge base plugin
            kb_plugin = self.plugin_manager.get_plugin("knowledge_base")
            if not kb_plugin:
                return None
            
            # Search for existing knowledge
            result = kb_plugin.search_knowledge(query)
            
            if result and "I don't have information" not in result:
                # Cache the result for quick access
                self.knowledge_cache[query.lower()] = result
                return f"📚 {result}"
            
            return None
            
        except Exception as e:
            print(f"Error checking knowledge base: {e}")
            return None
    
    def attempt_auto_learning(self, query: str) -> Optional[str]:
        """Attempt to automatically learn about the query"""
        try:
            # Get knowledge base plugin
            kb_plugin = self.plugin_manager.get_plugin("knowledge_base")
            if not kb_plugin or not kb_plugin.auto_learn:
                return None
            
            print(f"🧠 Auto-learning about: {query}")
            
            # Use the knowledge base's auto-learning capability
            if hasattr(kb_plugin, 'answer_question'):
                result = kb_plugin.answer_question(query)
                
                if result and "I couldn't find" not in result and "Error while learning" not in result:
                    # Cache the learned information
                    self.knowledge_cache[query.lower()] = result
                    return result
            
            return None
            
        except Exception as e:
            print(f"Error in auto-learning: {e}")
            return None
    
    def extract_and_store_knowledge(self, query: str, response: str):
        """Extract and store knowledge from successful responses"""
        try:
            # Only store if response seems informative
            if len(response) < 50 or self.indicates_unknown(response):
                return
            
            # Get knowledge base plugin
            kb_plugin = self.plugin_manager.get_plugin("knowledge_base")
            if not kb_plugin:
                return
            
            # Extract potential topic from query
            topic = self.extract_topic_from_query(query)
            if not topic:
                return
            
            # Create knowledge entry
            knowledge = {
                "topic": topic,
                "summary": response[:500],  # Limit length
                "details": [],
                "sources": ["assistant_response"],
                "confidence": 0.6  # Medium confidence for assistant responses
            }
            
            # Store the knowledge
            kb_plugin.store_knowledge(topic, knowledge, source="assistant", confidence=0.6)
            print(f"📚 Stored knowledge about: {topic}")
            
        except Exception as e:
            print(f"Error storing knowledge: {e}")
    
    def extract_topic_from_query(self, query: str) -> Optional[str]:
        """Extract the main topic from a query"""
        query_lower = query.lower()
        
        # Remove common question words and phrases
        remove_phrases = [
            "what is", "who is", "what are", "who are", "tell me about",
            "explain", "define", "definition of", "meaning of",
            "can you tell me", "do you know", "have you heard of",
            "the", "a", "an"
        ]
        
        cleaned_query = query_lower
        for phrase in remove_phrases:
            cleaned_query = cleaned_query.replace(phrase, "").strip()
        
        # Remove question marks and extra spaces
        cleaned_query = re.sub(r'[?!.]+', '', cleaned_query)
        cleaned_query = re.sub(r'\s+', ' ', cleaned_query).strip()
        
        # Take the main subject (first few words)
        words = cleaned_query.split()
        if len(words) > 0:
            # Take up to 3 words as the topic
            topic = ' '.join(words[:3])
            return topic if len(topic) > 2 else None
        
        return None
    
    def process_command_standard(self, user_input: str) -> str:
        """Standard command processing (the original process_command method)"""
        # This should call the original process_command method
        return self.process_command(user_input)
    
    def get_learning_stats(self) -> str:
        """Get statistics about learning progress"""
        try:
            kb_plugin = self.plugin_manager.get_plugin("knowledge_base")
            if not kb_plugin:
                return "❌ Knowledge base not available"
            
            entries = kb_plugin.knowledge_base.get("entries", {})
            total_entries = len(entries)
            
            if total_entries == 0:
                return "📚 No knowledge stored yet"
            
            # Calculate statistics
            auto_learned = sum(1 for entry in entries.values() if entry.get("source") == "web_search")
            manual_learned = sum(1 for entry in entries.values() if entry.get("source") == "manual")
            total_accesses = sum(entry.get("access_count", 0) for entry in entries.values())
            
            avg_confidence = sum(entry.get("confidence", 0) for entry in entries.values()) / total_entries
            
            stats = f"""📊 Learning Statistics:
            
📚 Total Knowledge Entries: {total_entries}
🤖 Auto-learned: {auto_learned}
👤 Manually taught: {manual_learned}
🔍 Total accesses: {total_accesses}
📈 Average confidence: {avg_confidence:.1%}
🧠 Cache size: {len(self.knowledge_cache)}"""
            
            return stats
            
        except Exception as e:
            return f"❌ Error getting learning stats: {e}"
    
    def enable_learning(self) -> str:
        """Enable automatic learning"""
        self.learning_enabled = True
        
        # Enable auto-learning in knowledge base plugin
        kb_plugin = self.plugin_manager.get_plugin("knowledge_base")
        if kb_plugin:
            kb_plugin.auto_learn = True
        
        return "✅ Automatic learning enabled"
    
    def disable_learning(self) -> str:
        """Disable automatic learning"""
        self.learning_enabled = False
        
        # Disable auto-learning in knowledge base plugin
        kb_plugin = self.plugin_manager.get_plugin("knowledge_base")
        if kb_plugin:
            kb_plugin.auto_learn = False
        
        return "❌ Automatic learning disabled"
    
    def clear_learning_cache(self) -> str:
        """Clear the learning cache"""
        self.knowledge_cache.clear()
        return "🗑️ Learning cache cleared"
