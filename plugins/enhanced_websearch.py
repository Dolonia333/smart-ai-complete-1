import webbrowser
import urllib.parse
import requests
from bs4 import BeautifulSoup
import json
import feedparser
import time
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from advanced_plugin_manager import BasePlugin
import re

class EnhancedWebSearchPlugin(BasePlugin):
    def __init__(self):
        super().__init__()
        self.description = "Advanced real-time web search with Google-like capabilities, news feeds, and live data"
        self.commands = ["search", "google", "news", "realtime", "live", "trending", "stock", "weather", "social", "reddit", "twitter", "prices", "images", "videos", "maps", "instant"]
        
        # API endpoints and configurations
        self.news_sources = [
            'https://feeds.bbci.co.uk/news/rss.xml',
            'https://rss.cnn.com/rss/edition.rss',
            'https://feeds.reuters.com/reuters/topNews',
            'https://feeds.npr.org/1001/rss.xml'
        ]
        
        # User agents for better scraping
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        }
    
    def handle_command(self, command: str, **kwargs) -> str:
        """Handle enhanced web search commands"""
        command_lower = command.lower()
        
        if "news" in command_lower or "breaking" in command_lower:
            return self.get_real_time_news(command)
        elif "trending" in command_lower or "viral" in command_lower:
            return self.get_trending_topics(command)
        elif "stock" in command_lower or "market" in command_lower or "$" in command:
            return self.get_stock_info(command)
        elif "reddit" in command_lower:
            return self.search_reddit(command)
        elif "twitter" in command_lower:
            return self.search_twitter(command)
        elif "price" in command_lower and ("compare" in command_lower or "check" in command_lower):
            return self.compare_prices(command)
        elif "images" in command_lower:
            return self.search_images(command)
        elif "videos" in command_lower:
            return self.search_videos(command)
        elif "maps" in command_lower or "location" in command_lower:
            return self.search_maps(command)
        elif "instant" in command_lower or "quick" in command_lower:
            return self.instant_answer(command)
        elif "realtime" in command_lower or "live" in command_lower:
            return self.real_time_search(command)
        elif any(word in command_lower for word in ["search", "google", "find"]):
            return self.enhanced_google_search(command)
        else:
            return self.show_advanced_help()
    
    def enhanced_google_search(self, command: str) -> str:
        """Enhanced Google search with result extraction and analysis"""
        try:
            query = self.extract_query(command)
            if not query:
                return "Please provide a search query. Example: 'search artificial intelligence news'"
            
            # Perform multiple search strategies
            results = []
            
            # 1. Direct Google search with result extraction
            google_results = self.scrape_google_results(query)
            if google_results:
                results.extend(google_results)
            
            # 2. Add related searches and suggestions
            suggestions = self.get_search_suggestions(query)
            
            # 3. Check for instant answers (like calculator, weather, etc.)
            instant = self.get_instant_answer(query)
            
            # Open main search in browser
            encoded_query = urllib.parse.quote(query)
            search_url = f"https://www.google.com/search?q={encoded_query}"
            webbrowser.open(search_url)
            
            # Format comprehensive response
            response = f"🔍 **Enhanced Search Results for '{query}'**\n\n"
            
            if instant:
                response += f"📋 **Instant Answer:** {instant}\n\n"
            
            if results:
                response += "🌐 **Top Search Results:**\n"
                for i, result in enumerate(results[:5], 1):
                    response += f"{i}. **{result['title']}**\n"
                    response += f"   {result['snippet']}\n"
                    response += f"   🔗 {result['url']}\n\n"
            
            if suggestions:
                response += f"💡 **Related Searches:** {', '.join(suggestions[:5])}\n\n"
            
            response += f"🌐 Full search opened in browser"
            return response
            
        except Exception as e:
            return f"❌ Error in enhanced search: {e}"
    
    def scrape_google_results(self, query: str, num_results: int = 10) -> list:
        """Scrape Google search results with enhanced parsing"""
        try:
            encoded_query = urllib.parse.quote(query)
            search_url = f"https://www.google.com/search?q={encoded_query}&num={num_results}"
            
            response = requests.get(search_url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            results = []
            
            # Enhanced result extraction
            for result in soup.find_all('div', class_='g'):
                try:
                    # Extract title
                    title_elem = result.find('h3')
                    if not title_elem:
                        continue
                    title = title_elem.get_text()
                    
                    # Extract URL
                    link_elem = result.find('a')
                    if not link_elem or not link_elem.get('href'):
                        continue
                    url = link_elem.get('href')
                    
                    # Extract snippet
                    snippet_elem = result.find('div', class_=['VwiC3b', 's3v9rd'])
                    snippet = snippet_elem.get_text() if snippet_elem else "No description available"
                    
                    # Extract additional metadata
                    date_elem = result.find('span', class_='f')
                    date = date_elem.get_text() if date_elem else ""
                    
                    results.append({
                        'title': title,
                        'url': url,
                        'snippet': snippet[:200] + "..." if len(snippet) > 200 else snippet,
                        'date': date
                    })
                    
                except Exception:
                    continue
            
            return results
            
        except Exception as e:
            print(f"Error scraping Google results: {e}")
            return []
    
    def get_real_time_news(self, command: str) -> str:
        """Get real-time news from multiple sources"""
        try:
            query = self.extract_query(command) if "about" in command else None
            news_items = []
            
            # Fetch from multiple RSS feeds
            for source_url in self.news_sources:
                try:
                    feed = feedparser.parse(source_url)
                    source_name = feed.feed.title if hasattr(feed.feed, 'title') else "News Source"
                    
                    for entry in feed.entries[:5]:  # Top 5 from each source
                        # Filter by query if provided
                        if query and query.lower() not in (entry.title + entry.summary).lower():
                            continue
                            
                        pub_date = entry.published if hasattr(entry, 'published') else "Recent"
                        news_items.append({
                            'title': entry.title,
                            'summary': entry.summary[:150] + "..." if len(entry.summary) > 150 else entry.summary,
                            'link': entry.link,
                            'source': source_name,
                            'date': pub_date
                        })
                except Exception:
                    continue
            
            # Sort by relevance/recency
            news_items = news_items[:10]  # Top 10 overall
            
            if not news_items:
                return "❌ Could not fetch real-time news at the moment"
            
            response = f"📰 **Real-Time News{f' about {query}' if query else ''}**\n\n"
            
            for i, item in enumerate(news_items, 1):
                response += f"{i}. **{item['title']}**\n"
                response += f"   📰 {item['source']} | 📅 {item['date']}\n"
                response += f"   {item['summary']}\n"
                response += f"   🔗 {item['link']}\n\n"
            
            return response
            
        except Exception as e:
            return f"❌ Error fetching news: {e}"
    
    def get_trending_topics(self, command: str) -> str:
        """Get trending topics from various platforms"""
        try:
            trends = []
            
            # Google Trends (simplified)
            try:
                trends_url = "https://trends.google.com/trends/trendingsearches/daily/rss"
                response = requests.get(trends_url, headers=self.headers, timeout=10)
                soup = BeautifulSoup(response.text, 'xml')
                
                for item in soup.find_all('item')[:10]:
                    title = item.find('title').text if item.find('title') else "Trending Topic"
                    trends.append({
                        'platform': 'Google Trends',
                        'topic': title,
                        'type': 'Search Trend'
                    })
            except Exception:
                pass
            
            # Reddit trending (from popular subreddits)
            try:
                reddit_trends = self.get_reddit_trending()
                trends.extend(reddit_trends)
            except Exception:
                pass
            
            if not trends:
                return "❌ Could not fetch trending topics at the moment"
            
            response = "🔥 **Trending Topics Right Now**\n\n"
            
            for i, trend in enumerate(trends[:15], 1):
                response += f"{i}. **{trend['topic']}**\n"
                response += f"   📱 {trend['platform']} | 🏷️ {trend['type']}\n\n"
            
            return response
            
        except Exception as e:
            return f"❌ Error fetching trends: {e}"
    
    def get_reddit_trending(self) -> list:
        """Get trending topics from Reddit"""
        try:
            trends = []
            reddit_url = "https://www.reddit.com/r/popular.json"
            
            response = requests.get(reddit_url, headers=self.headers, timeout=10)
            data = response.json()
            
            for post in data['data']['children'][:10]:
                post_data = post['data']
                trends.append({
                    'platform': 'Reddit',
                    'topic': post_data['title'],
                    'type': f"r/{post_data['subreddit']}"
                })
            
            return trends
        except Exception:
            return []
    
    def get_stock_info(self, command: str) -> str:
        """Get real-time stock information"""
        try:
            # Extract stock symbol
            symbols = re.findall(r'\$([A-Z]{1,5})', command.upper())
            if not symbols:
                # Try to extract from text
                words = command.upper().split()
                potential_symbols = [word for word in words if len(word) <= 5 and word.isalpha()]
                symbols = potential_symbols[:3]  # Max 3 symbols
            
            if not symbols:
                return "💰 Please specify a stock symbol. Example: 'stock AAPL' or 'market $TSLA'"
            
            response = "📈 **Stock Information**\n\n"
            
            for symbol in symbols:
                try:
                    # Using a free API (Alpha Vantage alternative or Yahoo Finance)
                    stock_url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
                    stock_response = requests.get(stock_url, headers=self.headers, timeout=10)
                    
                    if stock_response.status_code == 200:
                        data = stock_response.json()
                        if 'chart' in data and data['chart']['result']:
                            result = data['chart']['result'][0]
                            meta = result['meta']
                            
                            current_price = meta.get('regularMarketPrice', 'N/A')
                            prev_close = meta.get('previousClose', 'N/A')
                            change = current_price - prev_close if current_price != 'N/A' and prev_close != 'N/A' else 'N/A'
                            change_percent = (change / prev_close * 100) if change != 'N/A' and prev_close != 0 else 'N/A'
                            
                            response += f"🏢 **{symbol}** ({meta.get('longName', symbol)})\n"
                            response += f"💲 Current: ${current_price:.2f}\n"
                            response += f"📊 Change: ${change:.2f} ({change_percent:.2f}%)\n"
                            response += f"📅 Previous Close: ${prev_close:.2f}\n\n"
                        else:
                            response += f"❌ Could not fetch data for {symbol}\n\n"
                    else:
                        response += f"❌ Could not fetch data for {symbol}\n\n"
                        
                except Exception as e:
                    response += f"❌ Error fetching {symbol}: {str(e)[:50]}\n\n"
            
            return response
            
        except Exception as e:
            return f"❌ Error fetching stock information: {e}"
    
    def search_reddit(self, command: str) -> str:
        """Search Reddit for posts"""
        try:
            query = self.extract_query(command)
            if not query:
                return "🔍 Please provide a search query. Example: 'reddit search python programming'"
            
            # Reddit search API
            reddit_url = f"https://www.reddit.com/search.json?q={urllib.parse.quote(query)}&sort=hot&limit=10"
            response = requests.get(reddit_url, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                return "❌ Could not access Reddit search at the moment"
            
            data = response.json()
            posts = data['data']['children']
            
            if not posts:
                return f"❌ No Reddit posts found for '{query}'"
            
            result = f"🔴 **Reddit Search Results for '{query}'**\n\n"
            
            for i, post in enumerate(posts[:8], 1):
                post_data = post['data']
                title = post_data['title']
                subreddit = post_data['subreddit']
                score = post_data['score']
                comments = post_data['num_comments']
                url = f"https://reddit.com{post_data['permalink']}"
                
                result += f"{i}. **{title}**\n"
                result += f"   📍 r/{subreddit} | ⬆️ {score} | 💬 {comments} comments\n"
                result += f"   🔗 {url}\n\n"
            
            # Open Reddit search in browser
            reddit_search_url = f"https://www.reddit.com/search/?q={urllib.parse.quote(query)}"
            webbrowser.open(reddit_search_url)
            result += "🌐 Full Reddit search opened in browser"
            
            return result
            
        except Exception as e:
            return f"❌ Error searching Reddit: {e}"
    
    def search_images(self, command: str) -> str:
        """Search for images"""
        try:
            query = self.extract_query(command)
            if not query:
                return "🖼️ Please provide a search query. Example: 'images cute cats'"
            
            # Open Google Images
            encoded_query = urllib.parse.quote(query)
            images_url = f"https://www.google.com/search?tbm=isch&q={encoded_query}"
            webbrowser.open(images_url)
            
            return f"🖼️ Opened Google Images search for '{query}' in your browser"
            
        except Exception as e:
            return f"❌ Error searching images: {e}"
    
    def search_videos(self, command: str) -> str:
        """Search for videos across platforms"""
        try:
            query = self.extract_query(command)
            if not query:
                return "🎥 Please provide a search query. Example: 'videos cooking tutorial'"
            
            encoded_query = urllib.parse.quote(query)
            
            # Open YouTube and Google Videos
            youtube_url = f"https://www.youtube.com/results?search_query={encoded_query}"
            google_videos_url = f"https://www.google.com/search?tbm=vid&q={encoded_query}"
            
            webbrowser.open(youtube_url)
            webbrowser.open(google_videos_url)
            
            return f"🎥 Opened video search for '{query}' on YouTube and Google Videos"
            
        except Exception as e:
            return f"❌ Error searching videos: {e}"
    
    def search_maps(self, command: str) -> str:
        """Search for locations and maps"""
        try:
            query = self.extract_query(command)
            if not query:
                return "🗺️ Please provide a location. Example: 'maps Central Park New York'"
            
            encoded_query = urllib.parse.quote(query)
            maps_url = f"https://www.google.com/maps/search/{encoded_query}"
            webbrowser.open(maps_url)
            
            return f"🗺️ Opened Google Maps search for '{query}'"
            
        except Exception as e:
            return f"❌ Error searching maps: {e}"
    
    def instant_answer(self, command: str) -> str:
        """Get instant answers for quick queries"""
        try:
            query = self.extract_query(command).lower()
            
            # Calculator
            if any(op in query for op in ['+', '-', '*', '/', '=', 'calculate']):
                return self.calculate(query)
            
            # Time/Date
            if any(word in query for word in ['time', 'date', 'today', 'now']):
                return f"⏰ Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # Quick definitions
            if 'define' in query or 'what is' in query:
                return self.quick_definition(query)
            
            # Unit conversions
            if any(word in query for word in ['convert', 'to', 'celsius', 'fahrenheit', 'miles', 'kilometers']):
                return self.unit_conversion(query)
            
            return "❓ I couldn't find an instant answer for that query"
            
        except Exception as e:
            return f"❌ Error getting instant answer: {e}"
    
    def calculate(self, expression: str) -> str:
        """Simple calculator function"""
        try:
            # Clean and secure the expression
            cleaned = re.sub(r'[^0-9+\-*/().\s]', '', expression)
            if not cleaned:
                return "❌ Invalid calculation"
            
            result = eval(cleaned)
            return f"🧮 **Calculator:** {cleaned} = {result}"
        except Exception:
            return "❌ Invalid mathematical expression"
    
    def quick_definition(self, query: str) -> str:
        """Get quick definitions"""
        try:
            # Extract the term to define
            if 'define' in query:
                term = query.split('define')[-1].strip()
            elif 'what is' in query:
                term = query.split('what is')[-1].strip()
            else:
                return "❓ Please specify what you want to define"
            
            if not term:
                return "❓ Please specify what you want to define"
            
            # Try to get a quick definition from a dictionary API
            try:
                api_url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{term}"
                response = requests.get(api_url, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    if data and len(data) > 0:
                        word_data = data[0]
                        definitions = []
                        
                        for meaning in word_data.get('meanings', []):
                            for definition in meaning.get('definitions', []):
                                definitions.append(f"({meaning.get('partOfSpeech', 'n/a')}) {definition.get('definition', '')}")
                        
                        if definitions:
                            return f"📖 **{term}:**\n{definitions[0]}"
                
            except Exception:
                pass
            
            # Fallback to Google search
            encoded_term = urllib.parse.quote(f"define {term}")
            search_url = f"https://www.google.com/search?q={encoded_term}"
            webbrowser.open(search_url)
            
            return f"📖 Opened definition search for '{term}' in browser"
            
        except Exception as e:
            return f"❌ Error getting definition: {e}"
    
    def unit_conversion(self, query: str) -> str:
        """Basic unit conversions"""
        try:
            query_lower = query.lower()
            
            # Temperature conversions
            if 'celsius' in query_lower and 'fahrenheit' in query_lower:
                numbers = re.findall(r'-?\d+(?:\.\d+)?', query)
                if numbers:
                    if 'celsius' in query_lower.split(numbers[0])[0]:
                        # Celsius to Fahrenheit
                        celsius = float(numbers[0])
                        fahrenheit = (celsius * 9/5) + 32
                        return f"🌡️ {celsius}°C = {fahrenheit:.1f}°F"
                    else:
                        # Fahrenheit to Celsius
                        fahrenheit = float(numbers[0])
                        celsius = (fahrenheit - 32) * 5/9
                        return f"🌡️ {fahrenheit}°F = {celsius:.1f}°C"
            
            # Distance conversions
            elif 'miles' in query_lower and 'kilometer' in query_lower:
                numbers = re.findall(r'\d+(?:\.\d+)?', query)
                if numbers:
                    if 'miles' in query_lower.split(numbers[0])[0]:
                        # Miles to Kilometers
                        miles = float(numbers[0])
                        km = miles * 1.60934
                        return f"📏 {miles} miles = {km:.2f} kilometers"
                    else:
                        # Kilometers to Miles
                        km = float(numbers[0])
                        miles = km / 1.60934
                        return f"📏 {km} km = {miles:.2f} miles"
            
            return "🔄 Supported conversions: temperature (C/F), distance (miles/km)"
            
        except Exception as e:
            return f"❌ Error in conversion: {e}"
    
    def real_time_search(self, command: str) -> str:
        """Perform real-time search across multiple sources"""
        try:
            query = self.extract_query(command)
            if not query:
                return "🔄 Please provide a search query. Example: 'realtime search breaking news AI'"
            
            response = f"🔄 **Real-Time Search for '{query}'**\n\n"
            
            # 1. Get latest news
            news_results = self.get_real_time_news(f"news about {query}")
            if "Real-Time News" in news_results:
                response += news_results[:500] + "...\n\n"
            
            # 2. Get trending topics
            if any(word in query.lower() for word in ['trend', 'viral', 'popular']):
                trending = self.get_trending_topics(command)
                if "Trending Topics" in trending:
                    response += trending[:300] + "...\n\n"
            
            # 3. Social media search
            reddit_results = self.search_reddit(f"reddit {query}")
            if "Reddit Search Results" in reddit_results:
                response += reddit_results[:400] + "...\n\n"
            
            # 4. Regular web search
            web_results = self.enhanced_google_search(f"search {query}")
            if "Enhanced Search Results" in web_results:
                response += web_results[:500] + "..."
            
            return response
            
        except Exception as e:
            return f"❌ Error in real-time search: {e}"
    
    def get_search_suggestions(self, query: str) -> list:
        """Get search suggestions for a query"""
        try:
            # Google Suggest API
            suggest_url = f"http://suggestqueries.google.com/complete/search?client=chrome&q={urllib.parse.quote(query)}"
            response = requests.get(suggest_url, timeout=5)
            
            if response.status_code == 200:
                suggestions = response.json()
                if len(suggestions) > 1:
                    return suggestions[1][:5]  # Return first 5 suggestions
            
            return []
        except Exception:
            return []
    
    def get_instant_answer(self, query: str) -> str:
        """Try to get instant answers from query"""
        try:
            # Check for mathematical expressions
            if any(op in query for op in ['+', '-', '*', '/', '=']):
                return self.calculate(query)
            
            # Check for time queries
            if any(word in query.lower() for word in ['time', 'date', 'today']):
                return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            return None
        except Exception:
            return None
    
    def extract_query(self, command: str) -> str:
        """Extract search query from command"""
        remove_words = [
            "search", "google", "find", "news", "trending", "stock", "reddit", 
            "images", "videos", "maps", "instant", "realtime", "live", "for", 
            "about", "on", "of", "the", "and", "prices", "compare", "check"
        ]
        
        words = command.split()
        query_words = []
        
        for word in words:
            if word.lower() not in remove_words:
                query_words.append(word)
        
        return " ".join(query_words).strip()
    
    def show_advanced_help(self) -> str:
        """Show comprehensive help for enhanced search"""
        return """🚀 **Enhanced Web Search Commands:**

🔍 **General Search:**
• 'search [query]' - Enhanced Google search with results
• 'instant [query]' - Quick answers and calculations
• 'realtime [query]' - Real-time multi-source search

📰 **News & Trends:**
• 'news [topic]' - Real-time news from multiple sources  
• 'trending' - Current trending topics
• 'breaking news' - Latest breaking news

📈 **Financial:**
• 'stock AAPL' or '$AAPL' - Real-time stock information
• 'market updates' - Market overview

🌐 **Social & Media:**
• 'reddit [query]' - Search Reddit posts
• 'images [query]' - Image search
• 'videos [query]' - Video search across platforms

🗺️ **Location & Maps:**
• 'maps [location]' - Google Maps search
• 'location [place]' - Find places and directions

🧮 **Instant Tools:**
• Calculator: '2 + 2', 'calculate 15 * 8'
• Time: 'time now', 'date today'
• Definitions: 'define artificial intelligence'
• Conversions: '32 fahrenheit to celsius'

All searches open in browser with enhanced results displayed here!"""

# Create plugin instance
def create_plugin():
    """Factory function to create plugin instance."""
    return EnhancedWebSearchPlugin()

# Plugin registration
if __name__ == "__main__":
    plugin = create_plugin()
    print(f"Enhanced WebSearch Plugin v{plugin.version} loaded successfully!")
    print("Available commands:", len(plugin.commands))
