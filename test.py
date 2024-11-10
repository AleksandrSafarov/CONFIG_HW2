import unittest
from unittest.mock import patch, mock_open, MagicMock
import zlib
from datetime import datetime
import subprocess
import os

from main import (
    read_git_object,
    parse_commit_object,
    get_all_commits,
    build_commit_graph,
    generate_plantuml,
    save_plantuml_file,
    generate_graph_image,
)


class TestGitHistoryVisualizer(unittest.TestCase):
    
    @patch("builtins.open", new_callable=mock_open, read_data=zlib.compress(b'commit 123\n'))
    @patch("os.path.exists", return_value=True)
    def test_read_git_object(self, mock_exists, mock_open_file):
        repo_path = "fake_repo"
        object_hash = "abcd1234"
        
        decompressed_data = read_git_object(repo_path, object_hash)
        self.assertEqual(decompressed_data, b'commit 123\n')
    
    def test_parse_commit_object(self):
        commit_data = """tree abcd1234
parent efgh5678
author John Doe <johndoe@example.com> 1625140800 +0000

commit message
"""
        tree_hash, parents, author_time = parse_commit_object(commit_data)
        self.assertEqual(tree_hash, "abcd1234")
        self.assertEqual(parents, ["efgh5678"])
        self.assertEqual(author_time, 1625140800)

    def test_generate_plantuml(self):
        commit_graph = {
            "abcd1234": [],
            "efgh5678": ["abcd1234"]
        }
        plantuml_text = generate_plantuml(commit_graph)
        self.assertIn("@startuml", plantuml_text)
        self.assertIn("\"abcd1234 (1)\" --> \"efgh5678 (2)\"", plantuml_text)
        self.assertIn("@enduml", plantuml_text)

    @patch("builtins.open", new_callable=mock_open)
    def test_save_plantuml_file(self, mock_open_file):
        plantuml_text = "@startuml\nA --> B\n@enduml"
        plantuml_file_path = "test.puml"
        
        save_plantuml_file(plantuml_text, plantuml_file_path)
        mock_open_file.assert_called_once_with(plantuml_file_path, 'w')
        mock_open_file().write.assert_called_once_with(plantuml_text)

    @patch("subprocess.run")
    @patch("os.rename")
    def test_generate_graph_image(self, mock_rename, mock_subprocess_run):
        mock_subprocess_run.return_value = subprocess.CompletedProcess(args=[], returncode=0)
        
        plantuml_file_path = "test.puml"
        output_image_path = "test.png"
        plantuml_jar_path = "plantuml.jar"
        
        generate_graph_image(plantuml_file_path, output_image_path, plantuml_jar_path)
        mock_subprocess_run.assert_called_once_with(
            ['java', '-jar', plantuml_jar_path, plantuml_file_path, '-tpng', '-o', os.path.dirname(output_image_path)],
            capture_output=True, text=True
        )
        mock_rename.assert_called_once_with("test.png", output_image_path)


if __name__ == "__main__":
    unittest.main()
