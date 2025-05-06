import os
import tempfile
import unittest
from pathlib import Path
import shutil
from click.testing import CliRunner
from unittest.mock import patch, MagicMock

# Import le module à tester
from file_cleaner import find_files_with_extension, delete_file, count_files_by_extension
from file_cleaner import cli, search_command, analyze_command


class TestFileCleaner(unittest.TestCase):
    """Tests unitaires pour le module file_cleaner."""

    def setUp(self):
        """Crée un répertoire temporaire et des fichiers de test."""
        # Créer un répertoire temporaire
        self.temp_dir = tempfile.mkdtemp()
        
        # Créer des fichiers de test
        self.test_files = {
            'test1.txt': 'Contenu du fichier test1.txt',
            'test2.txt': 'Contenu du fichier test2.txt',
            'document.pdf': 'Faux contenu PDF',
            'image.jpg': 'Faux contenu JPG',
            'script.py': 'print("Hello World")',
        }
        
        for filename, content in self.test_files.items():
            with open(os.path.join(self.temp_dir, filename), 'w') as f:
                f.write(content)

    def tearDown(self):
        """Supprime le répertoire temporaire."""
        shutil.rmtree(self.temp_dir)

    def test_find_files_with_extension(self):
        """Teste la fonction find_files_with_extension."""
        # Test avec extension .txt
        directory, files = find_files_with_extension(Path(self.temp_dir), '.txt', 'asc')
        self.assertEqual(len(files), 2)
        self.assertIn('test1.txt', files)
        self.assertIn('test2.txt', files)
        
        # Test sans le point dans l'extension
        directory, files = find_files_with_extension(Path(self.temp_dir), 'pdf', 'asc')
        self.assertEqual(len(files), 1)
        self.assertIn('document.pdf', files)
        
        # Test de tri croissant
        directory, files = find_files_with_extension(Path(self.temp_dir), 'txt', 'asc')
        self.assertEqual(files, ['test1.txt', 'test2.txt'])
        
        # Test de tri décroissant
        directory, files = find_files_with_extension(Path(self.temp_dir), 'txt', 'desc')
        self.assertEqual(files, ['test2.txt', 'test1.txt'])

    def test_find_files_nonexistent_directory(self):
        """Teste la recherche dans un répertoire inexistant."""
        from click import BadParameter
        
        with self.assertRaises(BadParameter):
            find_files_with_extension(Path('/nonexistent/dir'), 'txt', 'asc')

    def test_find_files_no_matches(self):
        """Teste le cas où aucun fichier ne correspond à l'extension."""
        from click import BadParameter
        
        with self.assertRaises(BadParameter):
            find_files_with_extension(Path(self.temp_dir), 'xlsx', 'asc')

    @patch('file_cleaner.send2trash.send2trash')
    def test_delete_file(self, mock_send2trash):
        """Teste la fonction delete_file."""
        # Test de suppression d'un fichier existant
        result = delete_file(Path(self.temp_dir), 'test1.txt')
        self.assertTrue(result)
        mock_send2trash.assert_called_once_with(str(Path(self.temp_dir) / 'test1.txt'))
        
        # Test de suppression d'un fichier inexistant
        result = delete_file(Path(self.temp_dir), 'nonexistent.txt')
        self.assertFalse(result)

    def test_count_files_by_extension(self):
        """Teste la fonction count_files_by_extension."""
        extensions = count_files_by_extension(Path(self.temp_dir))
        
        self.assertEqual(extensions['.txt'], 2)
        self.assertEqual(extensions['.pdf'], 1)
        self.assertEqual(extensions['.jpg'], 1)
        self.assertEqual(extensions['.py'], 1)

    def test_cli_search_command(self):
        """Teste la commande search via l'interface CLI."""
        runner = CliRunner()
        
        # Test de la recherche de fichiers .txt
        result = runner.invoke(search_command, [self.temp_dir, 'txt'])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('test1.txt', result.output)
        self.assertIn('test2.txt', result.output)
        
        # Test avec l'option --delete (simulée avec une confirmation non)
        with patch('builtins.input', return_value='n'):
            result = runner.invoke(search_command, [self.temp_dir, 'txt', '--delete', '--confirm'])
            self.assertEqual(result.exit_code, 0)
            self.assertIn('Fichiers à supprimer', result.output)

    def test_cli_analyze_command(self):
        """Teste la commande analyze via l'interface CLI."""
        runner = CliRunner()
        
        result = runner.invoke(analyze_command, [self.temp_dir])
        self.assertEqual(result.exit_code, 0)
        self.assertIn('.txt', result.output)
        self.assertIn('2 fichier(s)', result.output)
        self.assertIn('Total', result.output)
        self.assertIn('5 fichier(s)', result.output)


if __name__ == '__main__':
    unittest.main()