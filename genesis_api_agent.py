#!/usr/bin/env python3
"""
Genesis API Reference Agent

This agent integrates all API documentation from the api_reference directory
and provides a convenient interface for users to query and access API information.
"""

import os
import re
import glob
from typing import Dict, List, Any, Optional
import json

class GenesisAPIAgent:
    """
    Genesis API Reference Agent that loads and processes all API documentation.
    """
    
    def __init__(self, docs_path: str = "source/api_reference"):
        """
        Initialize the agent and load all documentation.
        
        Args:
            docs_path: Path to the API reference documentation
        """
        self.docs_path = docs_path
        self.knowledge_base: Dict[str, Any] = {
            "entities": {},
            "materials": {},
            "options": {},
            "scene": {},
            "sensor": {},
            "solvers": {},
            "boundaries": {},
            "couplers": {},
            "states": {}
        }
        self.documents: List[Dict[str, Any]] = []
        
        # Load all documentation
        self._load_documents()
        
        # Build knowledge base
        self._build_knowledge_base()
    
    def _load_documents(self) -> None:
        """
        Load all Markdown documents from the api_reference directory.
        """
        md_files = glob.glob(os.path.join(self.docs_path, "**/*.md"), recursive=True)
        
        # Map directory names to knowledge base categories
        category_map = {
            "entity": "entities",
            "material": "materials",
            "options": "options", 
            "scene": "scene",
            "sensor": "sensor",
            "solvers": "solvers",
            "boundaries": "boundaries",
            "couplers": "couplers",
            "states": "states"
        }
        
        for md_file in md_files:
            relative_path = os.path.relpath(md_file, self.docs_path)
            dir_name = relative_path.split(os.sep)[0]
            
            # Map directory name to category
            category = category_map.get(dir_name, dir_name)
            
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            document = {
                "file_path": md_file,
                "relative_path": relative_path,
                "category": category,
                "content": content,
                "title": self._extract_title(content)
            }
            
            self.documents.append(document)
    
    def _extract_title(self, content: str) -> Optional[str]:
        """
        Extract the title from Markdown content.
        
        Args:
            content: Markdown content
            
        Returns:
            Extracted title or None if not found
        """
        match = re.match(r"^#\s+(.*)$", content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        return None
    
    def _build_knowledge_base(self) -> None:
        """
        Build a structured knowledge base from the loaded documents.
        """
        for doc in self.documents:
            category = doc["category"]
            title = doc["title"]
            
            if not title:
                continue
            
            # Extract API name from title (remove backticks if present)
            api_name = title.strip("`")
            
            # Extract summary
            summary = self._extract_summary(doc["content"])
            
            # Extract code examples
            examples = self._extract_code_examples(doc["content"])
            
            # Extract parameters
            parameters = self._extract_parameters(doc["content"])
            
            # Extract inheritance
            inheritance = self._extract_inheritance(doc["content"])
            
            # Store in knowledge base
            if category in self.knowledge_base:
                self.knowledge_base[category][api_name] = {
                    "title": title,
                    "summary": summary,
                    "examples": examples,
                    "parameters": parameters,
                    "inheritance": inheritance,
                    "file_path": doc["file_path"],
                    "relative_path": doc["relative_path"],
                    "content": doc["content"]
                }
    
    def _extract_summary(self, content: str) -> Optional[str]:
        """
        Extract summary from document content.
        
        Args:
            content: Markdown content
            
        Returns:
            Extracted summary or None if not found
        """
        lines = content.split("\n")
        summary_lines = []
        in_summary = False
        
        for line in lines:
            stripped_line = line.strip()
            
            # Look for overview section
            if stripped_line.startswith("## 概述") or stripped_line.startswith("## Overview"):
                in_summary = True
                continue
            
            # Stop at the next heading or code block
            if in_summary:
                if stripped_line.startswith("##") or stripped_line.startswith("```"):
                    break
                if stripped_line:
                    summary_lines.append(stripped_line)
        
        # If no overview section found, try fallback to description after title
        if not summary_lines:
            in_fallback = False
            for line in lines:
                stripped_line = line.strip()
                
                # Start after the title
                if stripped_line.startswith("#") and not in_fallback:
                    in_fallback = True
                    continue
                
                # Stop at the next heading or code block
                if in_fallback:
                    if stripped_line.startswith("##") or stripped_line.startswith("```"):
                        break
                    if stripped_line:
                        summary_lines.append(stripped_line)
        
        if summary_lines:
            return " ".join(summary_lines)
        return None
    
    def _extract_code_examples(self, content: str) -> List[str]:
        """
        Extract code examples from document content.
        
        Args:
            content: Markdown content
            
        Returns:
            List of code examples
        """
        examples = []
        code_blocks = re.findall(r"```python(.*?)```", content, re.DOTALL)
        
        for block in code_blocks:
            examples.append(block.strip())
        
        return examples
    
    def _extract_parameters(self, content: str) -> List[Dict[str, str]]:
        """
        Extract parameters from document content.
        
        Args:
            content: Markdown content
            
        Returns:
            List of parameter dictionaries
        """
        parameters = []
        
        # Look for parameter tables
        table_pattern = r"##.*参数.*\n(.*?)\n(?:##|```|$)" 
        matches = re.findall(table_pattern, content, re.DOTALL)
        
        for table_content in matches:
            # Parse table
            lines = table_content.strip().split("\n")
            if len(lines) < 3:
                continue
            
            # Skip header and separator lines
            for line in lines[2:]:
                if not line.strip():
                    continue
                    
                # Split by pipe, ignoring leading/trailing pipes
                parts = [p.strip() for p in line.strip("|").split("|")]
                if len(parts) >= 3:
                    parameter = {
                        "name": parts[0],
                        "type": parts[1],
                        "description": parts[2]
                    }
                    parameters.append(parameter)
        
        return parameters
    
    def _extract_inheritance(self, content: str) -> Optional[str]:
        """
        Extract inheritance information from document content.
        
        Args:
            content: Markdown content
            
        Returns:
            Extracted inheritance string or None if not found
        """
        inheritance_pattern = r"##.*继承关系.*\n```\n(.*?)```" 
        match = re.search(inheritance_pattern, content, re.DOTALL)
        
        if match:
            return match.group(1).strip()
        return None
    
    def search(self, query: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for API information based on query.
        
        Args:
            query: Search query
            category: Optional category filter (entities, materials, options, scene, sensor)
            
        Returns:
            List of matching API entries
        """
        results = []
        query_lower = query.lower()
        
        # Determine which categories to search
        categories_to_search = [category] if category else self.knowledge_base.keys()
        
        for cat in categories_to_search:
            if cat not in self.knowledge_base:
                continue
            
            for api_name, api_info in self.knowledge_base[cat].items():
                # Search in title, summary, parameters
                if (query_lower in api_name.lower() or 
                    (api_info["summary"] and query_lower in api_info["summary"].lower()) or
                    any(query_lower in p["name"].lower() for p in api_info["parameters"])):
                    
                    results.append({
                        "category": cat,
                        "api_name": api_name,
                        "title": api_info["title"],
                        "summary": api_info["summary"],
                        "parameters": api_info["parameters"],
                        "inheritance": api_info["inheritance"],
                        "file_path": api_info["file_path"]
                    })
        
        return results
    
    def get_api_info(self, api_name: str, category: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific API.
        
        Args:
            api_name: Name of the API to retrieve
            category: Optional category filter
            
        Returns:
            API information dictionary or None if not found
        """
        api_name_lower = api_name.lower()
        
        # Determine which categories to search
        categories_to_search = [category] if category else self.knowledge_base.keys()
        
        for cat in categories_to_search:
            if cat not in self.knowledge_base:
                continue
            
            for name, info in self.knowledge_base[cat].items():
                if api_name_lower == name.lower() or api_name_lower == info["title"].strip("`").lower():
                    return {
                        "category": cat,
                        "api_name": name,
                        **info
                    }
        
        return None
    
    def list_apis(self, category: Optional[str] = None) -> List[str]:
        """
        List all APIs in the knowledge base.
        
        Args:
            category: Optional category filter
            
        Returns:
            List of API names
        """
        apis = []
        
        categories_to_list = [category] if category else self.knowledge_base.keys()
        
        for cat in categories_to_list:
            if cat not in self.knowledge_base:
                continue
            
            for api_name in self.knowledge_base[cat].keys():
                apis.append(f"{cat}.{api_name}")
        
        return apis
    
    def export_knowledge_base(self, output_path: str = "genesis_api_knowledge_base.json") -> None:
        """
        Export the knowledge base to a JSON file.
        
        Args:
            output_path: Path to the output JSON file
        """
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.knowledge_base, f, indent=2, ensure_ascii=False)
    
    def interactive_mode(self) -> None:
        """
        Start interactive mode for user queries.
        """
        print("\n=== Genesis API Reference Agent ===")
        print("Type 'help' for available commands, 'exit' to quit.")
        print("=" * 50)
        
        while True:
            try:
                user_input = input("\n> ").strip()
                
                if user_input.lower() == "exit":
                    print("Goodbye!")
                    break
                
                elif user_input.lower() == "help":
                    self._show_help()
                
                elif user_input.lower().startswith("list"):
                    parts = user_input.split()
                    category = parts[1] if len(parts) > 1 else None
                    self._list_apis(category)
                
                elif user_input.lower().startswith("search"):
                    query = user_input[7:].strip()
                    if query:
                        self._search(query)
                    else:
                        print("Please provide a search query.")
                
                elif user_input.lower().startswith("get"):
                    api_name = user_input[4:].strip()
                    if api_name:
                        self._get_api_info(api_name)
                    else:
                        print("Please provide an API name.")
                
                elif user_input.lower() == "categories":
                    self._list_categories()
                
                else:
                    # Treat as natural language query
                    self._natural_language_query(user_input)
                    
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def _show_help(self) -> None:
        """
        Show help information.
        """
        print("\nAvailable commands:")
        print("  help          - Show this help message")
        print("  exit          - Exit the agent")
        print("  categories    - List all categories")
        print("  list [category] - List all APIs (optionally filtered by category)")
        print("  search <query> - Search for APIs matching query")
        print("  get <api_name> - Get detailed information about an API")
        print("  <natural language> - Ask a question about the API")
    
    def _list_categories(self) -> None:
        """
        List all categories.
        """
        print("\nCategories:")
        for category in self.knowledge_base.keys():
            count = len(self.knowledge_base[category])
            print(f"  - {category}: {count} APIs")
    
    def _list_apis(self, category: Optional[str] = None) -> None:
        """
        List APIs in interactive mode.
        """
        apis = self.list_apis(category)
        
        if not apis:
            print("No APIs found.")
            return
        
        print(f"\nAPIs ({len(apis)} total):")
        for i, api in enumerate(apis, 1):
            print(f"  {i}. {api}")
    
    def _search(self, query: str) -> None:
        """
        Search APIs in interactive mode.
        """
        results = self.search(query)
        
        if not results:
            print("No results found.")
            return
        
        print(f"\nSearch results for '{query}' ({len(results)} total):")
        for i, result in enumerate(results, 1):
            print(f"  {i}. {result['api_name']} ({result['category']})")
            if result['summary']:
                print(f"     {result['summary'][:100]}...")
    
    def _get_api_info(self, api_name: str) -> None:
        """
        Get API info in interactive mode.
        """
        api_info = self.get_api_info(api_name)
        
        if not api_info:
            print(f"API '{api_name}' not found.")
            return
        
        print(f"\n=== {api_info['title']} ===")
        print(f"Category: {api_info['category']}")
        
        if api_info['summary']:
            print(f"\nSummary:")
            print(f"  {api_info['summary']}")
        
        if api_info['inheritance']:
            print(f"\nInheritance:")
            print(f"  {api_info['inheritance']}")
        
        if api_info['parameters']:
            print(f"\nParameters:")
            for param in api_info['parameters']:
                print(f"  - {param['name']} ({param['type']}): {param['description']}")
        
        if api_info['examples']:
            print(f"\nCode Examples:")
            for i, example in enumerate(api_info['examples'], 1):
                print(f"  Example {i}:")
                print(f"  ```python")
                print(f"{example[:200]}...")  # Show first 200 chars
                print(f"  ```")
    
    def _natural_language_query(self, query: str) -> None:
        """
        Handle natural language queries.
        
        Args:
            query: Natural language query
        """
        # Simple implementation for now - can be enhanced with NLP
        print("\nNatural language query handling is not fully implemented yet.")
        print("Please use the 'search' or 'get' commands for more precise results.")
        
        # Fallback to search
        self._search(query)

def main():
    """
    Main function to run the agent.
    """
    agent = GenesisAPIAgent()
    agent.interactive_mode()

if __name__ == "__main__":
    main()
