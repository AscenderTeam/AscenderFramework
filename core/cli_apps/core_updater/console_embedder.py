from rich.tree import Tree

class ConsoleEmbedder:
    
    def embed_core_files(self, tree: Tree, files: list[dict[str, str | bool]]):
        
        for core_file in files:
            tree_item = tree.add(core_file["name"], style="yellow" if core_file["is_dir"] else "green")
            if core_file["is_dir"]:
                self.embed_core_files(tree_item, core_file["children"])
        
        return tree
    
    def embed_checked_files(self, tree: Tree, files: list[dict[str, str | bool]]):
        
        for core_file in files:
            tree_item = tree.add(core_file["name"], style="green" if core_file["is_healthy"] else "red")
            if core_file["is_dir"]:
                self.embed_checked_files(tree_item, core_file["children"])
        
        return tree