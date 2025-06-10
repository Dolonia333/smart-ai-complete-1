import webbrowser
import urllib.parse
import requests
from bs4 import BeautifulSoup
from advanced_plugin_manager import BasePlugin

class WebSearchPlugin(BasePlugin):
    def __init__(self):
        super().__init__()
        self.description = "Search the web and open websites"
        self.commands = ["search", "google", "website", "open", "browse", "youtube", "wiki", "wikipedia"]
    
    def handle_command(self, command: str, **kwargs) -> str:
        """Handle web search and browsing commands"""
        command_lower = command.lower()
        
        if "youtube" in command_lower:
            return self.search_youtube(command)
        elif any(word in command_lower for word in ["wiki", "wikipedia"]):
            return self.search_wikipedia(command)
        elif "open" in command_lower and any(domain in command_lower for domain in [".com", ".org", ".net", "www"]):
            return self.open_website(command)
        elif any(word in command_lower for word in ["search", "google", "find"]):
            return self.search_google(command)
        else:
            return "Web commands: 'search [query]', 'open [website]', 'youtube [query]', 'wikipedia [topic]'"
    
    def extract_query(self, command: str) -> str:
        """Extract search query from command"""
        # Remove command words to get the actual query
        remove_words = ["search", "google", "find", "youtube", "wikipedia", "wiki", "open", "for", "about"]
        words = command.split()
        query_words = []
        
        for word in words:
            if word.lower() not in remove_words:
                query_words.append(word)
        
        return " ".join(query_words).strip()
    
    def search_google(self, command: str) -> str:
        """Search Google for a query"""
        try:
            query = self.extract_query(command)
            if not query:
                return "Please provide a search query. Example: 'search python programming'"
            
            # URL encode the query
            encoded_query = urllib.parse.quote(query)
            search_url = f"https://www.google.com/search?q={encoded_query}"
            
            # Open in browser
            webbrowser.open(search_url)
            
            # Try to get first few results
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                response = requests.get(search_url, headers=headers, timeout=5)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract first few search result titles
                results = []
                for h3 in soup.find_all('h3', limit=3):
                    if h3.text.strip():
                        results.append(h3.text.strip())
                
                if results:
                    result_text = f"Opened Google search for '{query}'. Top results:\n"
                    for i, result in enumerate(results, 1):
                        result_text += f"{i}. {result}\n"
                    return result_text
                
            except Exception:
                pass  # If scraping fails, just return basic message
            
            return f"Opened Google search for '{query}' in your browser"
            
        except Exception as e:
            return f"Error searching Google: {e}"
    
    def search_youtube(self, command: str) -> str:
        """Search YouTube for a query"""
        try:
            query = self.extract_query(command)
            if not query:
                return "Please provide a search query. Example: 'youtube python tutorial'"
            
            encoded_query = urllib.parse.quote(query)
            youtube_url = f"https://www.youtube.com/results?search_query={encoded_query}"
            
            webbrowser.open(youtube_url)
            return f"Opened YouTube search for '{query}' in your browser"
            
        except Exception as e:
            return f"Error searching YouTube: {e}"
    
    def search_wikipedia(self, command: str) -> str:
        """Search Wikipedia for a topic"""
        try:
            query = self.extract_query(command)
            if not query:
                return "Please provide a topic. Example: 'wikipedia artificial intelligence'"
            
            # Try to get Wikipedia summary
            try:
                import wikipedia
                summary = wikipedia.summary(query, sentences=2)
                wiki_url = wikipedia.page(query).url
                webbrowser.open(wiki_url)
                return f"Wikipedia: {summary}\n\nOpened full article in browser."
            except ImportError:
                # Fallback to direct URL if wikipedia package not available
                encoded_query = urllib.parse.quote(query.replace(" ", "_"))
                wiki_url = f"https://en.wikipedia.org/wiki/{encoded_query}"
                webbrowser.open(wiki_url)
                return f"Opened Wikipedia article for '{query}' in your browser"
            except Exception:
                # Fallback to search if exact page not found
                encoded_query = urllib.parse.quote(query)
                search_url = f"https://en.wikipedia.org/wiki/Special:Search?search={encoded_query}"
                webbrowser.open(search_url)
                return f"Opened Wikipedia search for '{query}' in your browser"
                
        except Exception as e:
            return f"Error searching Wikipedia: {e}"
    
    def open_website(self, command: str) -> str:
        """Open a specific website"""
        try:
            # Extract URL from command
            words = command.split()
            url = None
            
            for word in words:
                if any(domain in word.lower() for domain in [".com", ".org", ".net", ".gov", ".edu"]) or word.startswith("www."):
                    url = word
                    break
            
            if not url:
                return "Please provide a valid website URL. Example: 'open google.com'"
            
            # Add protocol if missing
            if not url.startswith(("http://", "https://")):
                url = "https://" + url
            
            webbrowser.open(url)
            return f"Opened {url} in your browser"
            
        except Exception as e:
            return f"Error opening website: {e}"
    
    def get_quick_search_engines(self) -> str:
        """Get list of quick search options"""
        return """Quick search options:
        - 'search [query]' - Google search
        - 'youtube [query]' - YouTube search  
        - 'wikipedia [topic]' - Wikipedia lookup
        - 'open [website]' - Open specific website"""
