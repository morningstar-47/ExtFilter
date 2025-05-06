import click
import os
import send2trash
from pathlib import Path
import random
import logging
from typing import List, Tuple, Optional


# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def find_files_with_extension(directory: Path, extension: str, sort_order: str = 'asc') -> Tuple[Path, List[str]]:
    """
    Retourne une liste des fichiers avec l'extension donnée dans le répertoire donné.
    
    Args:
        directory: Chemin du répertoire à parcourir
        extension: Extension des fichiers à rechercher (avec ou sans le point)
        sort_order: Ordre de tri ('asc', 'desc' ou 'random')
        
    Returns:
        Tuple contenant le chemin du répertoire et la liste des fichiers trouvés
        
    Raises:
        click.BadParameter: Si le répertoire n'existe pas ou si aucun fichier n'est trouvé
    """
    if not directory.exists():
        raise click.BadParameter(f"Le dossier '{directory}' n'existe pas.")
    
    if not directory.is_dir():
        raise click.BadParameter(f"'{directory}' n'est pas un dossier.")

    # Vérifier que l'extension est valide
    if not extension:
        raise click.BadParameter("L'extension doit être spécifiée.")
    
    # Normaliser l'extension (ajouter le point si nécessaire)
    if not extension.startswith("."):
        extension = f".{extension}"

    # Récupérer la liste des noms de fichiers avec l'extension donnée
    try:
        files = [entry.name for entry in os.scandir(directory) 
                if entry.is_file() and entry.name.lower().endswith(extension.lower())]
    except PermissionError:
        raise click.BadParameter(f"Impossible d'accéder au dossier '{directory}': permission refusée.")
    except Exception as e:
        raise click.BadParameter(f"Erreur lors de la lecture du dossier '{directory}': {e}")
        
    if not files:
        raise click.BadParameter(
            f"Aucun fichier avec l'extension '{extension}' trouvé dans le dossier '{directory}'.")

    # Trier la liste selon l'ordre spécifié
    if sort_order == "asc":
        files.sort()
    elif sort_order == "desc":
        files.sort(reverse=True)
    elif sort_order == "random":
        random.shuffle(files)
    else:
        raise click.BadParameter(
            "L'ordre de tri doit être 'asc', 'desc' ou 'random'.")
            
    logger.info(f"Trouvé {len(files)} fichier(s) avec l'extension '{extension}' dans '{directory}'")
    return directory, files


def delete_file(directory_path: Path, file: str) -> bool:
    """
    Supprime un fichier en l'envoyant à la corbeille.
    
    Args:
        directory_path: Chemin du répertoire contenant le fichier
        file: Nom du fichier à supprimer
        
    Returns:
        bool: True si la suppression a réussi, False sinon
    """
    file_path = directory_path.joinpath(file)
    
    if not file_path.exists():
        click.echo(f"Le fichier '{file}' n'existe pas.")
        return False

    try:
        send2trash.send2trash(str(file_path))
        click.echo(f"Le fichier '{file}' a été envoyé dans la corbeille.")
        logger.info(f"Fichier supprimé: {file_path}")
        return True
    except Exception as e:
        click.echo(f"Erreur lors de la mise à la corbeille du fichier '{file}': {e}")
        logger.error(f"Erreur de suppression pour {file_path}: {e}")
        return False


def delete_files(directory_path: Path, files: List[str], confirm: bool = False) -> None:
    """
    Supprime tous les fichiers de la liste.
    
    Args:
        directory_path: Chemin du répertoire contenant les fichiers
        files: Liste des noms de fichiers à supprimer
        confirm: Si True, demande confirmation avant chaque suppression
    """
    # Afficher une liste des fichiers à supprimer
    click.echo(f"\nFichiers à supprimer ({len(files)}):")
    for i, file in enumerate(files, 1):
        click.echo(f"{i}. {file}")
    
    # Confirmation globale si beaucoup de fichiers
    if len(files) > 5 and confirm:
        prompt = input(f"\nVoulez-vous vraiment supprimer ces {len(files)} fichiers ? [o/N] ")
        if prompt.lower() not in ["o", "oui"]:
            click.echo("Opération annulée.")
            return

    # Suppression des fichiers
    deleted_count = 0
    for file in files:
        if confirm and len(files) <= 5:
            prompt = input(f"\nVoulez-vous supprimer le fichier '{file}' ? [o/N] ")
            if prompt.lower() not in ["o", "oui"]:
                click.echo(f"Le fichier '{file}' a été ignoré.")
                continue
        
        if delete_file(directory_path, file):
            deleted_count += 1
    
    click.echo(f"\n{deleted_count} fichier(s) supprimé(s) sur {len(files)}.")


def display_files_content(directory_path: Path, files: List[str], confirm: bool = False) -> None:
    """
    Affiche la liste des fichiers dans le dossier et permet d'afficher le contenu de chaque fichier.
    
    Args:
        directory_path: Chemin du répertoire contenant les fichiers
        files: Liste des noms de fichiers à afficher
        confirm: Si True, demande confirmation avant d'afficher le contenu de chaque fichier
    """
    click.echo(f"\nListe des fichiers dans le dossier '{directory_path}':")
    click.echo(f"* {len(files)} fichier(s) trouvé(s) *")
    click.echo("─" * 50)

    # Affichage de la liste des fichiers
    if len(files) > 10:
        # Affichage en colonnes pour une meilleure lisibilité
        num_cols = min(4, len(files))
        files_per_col = (len(files) + num_cols - 1) // num_cols
        
        for i in range(0, len(files), files_per_col):
            chunk = files[i:i + files_per_col]
            for j, file in enumerate(chunk):
                # Tronquer les noms de fichiers trop longs
                short_file = file[:17] + '...' if len(file) > 20 else file
                click.echo(f"{i+j+1:3d}. {short_file:<20}", nl=False)
            click.echo()
    else:
        # Affichage simple pour un petit nombre de fichiers
        for i, file in enumerate(files, 1):
            click.echo(f"{i}. {file}")

    # Affichage du contenu des fichiers
    if confirm:
        for file in files:
            user_input = input(f"\nVoulez-vous afficher le contenu du fichier '{file}' ? [o/N] ")
            if user_input.lower() not in ['o', 'oui']:
                continue

            # Afficher le contenu du fichier
            file_path = directory_path.joinpath(file)
            click.echo(f"\nContenu du fichier '{file}' :")
            click.echo("─" * 50)
            
            try:
                # Essayer de lire le fichier comme texte
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                    
                    # Limiter l'affichage pour les très grands fichiers
                    if len(content) > 10000:
                        click.echo(content[:10000])
                        click.echo("\n[...] Le contenu est trop volumineux, affichage tronqué.")
                    else:
                        click.echo(content)
            except UnicodeDecodeError:
                click.echo("[Erreur] Ce fichier n'est pas un fichier texte lisible.")
            except Exception as e:
                click.echo(f"[Erreur] Lecture du fichier '{file}': {e}")
            
            click.echo("─" * 50)
    else:
        # Sans confirmation, afficher tous les fichiers directement
        for file in files:
            file_path = directory_path.joinpath(file)
            click.echo(f"\nContenu du fichier '{file}' :")
            click.echo("─" * 50)
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                    if len(content) > 5000:
                        click.echo(content[:5000])
                        click.echo("\n[...] Le contenu est trop volumineux, affichage tronqué.")
                    else:
                        click.echo(content)
            except Exception as e:
                click.echo(f"[Erreur] Lecture du fichier '{file}': {e}")
            
            click.echo("─" * 50)


def count_files_by_extension(directory: Path) -> dict:
    """
    Compte le nombre de fichiers par extension dans un répertoire.
    
    Args:
        directory: Chemin du répertoire à analyser
        
    Returns:
        dict: Dictionnaire avec les extensions comme clés et le nombre de fichiers comme valeurs
    """
    extensions = {}
    
    try:
        for entry in os.scandir(directory):
            if entry.is_file():
                _, ext = os.path.splitext(entry.name)
                ext = ext.lower()
                if ext:
                    extensions[ext] = extensions.get(ext, 0) + 1
    except Exception as e:
        click.echo(f"Erreur lors de l'analyse du répertoire: {e}")
    
    return extensions


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """Utilitaire de gestion de fichiers par extension."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command('search')
@click.argument('directory', type=click.Path(exists=True))
@click.argument('extension')
@click.option('-d', '--delete', is_flag=True, help='Supprime les fichiers.')
@click.option('-c', '--confirm', is_flag=True, help='Demande confirmation.')
@click.option('-p', '--display', is_flag=True, help='Affiche le contenu.')
@click.option('-s', '--sort-order', type=click.Choice(['asc', 'desc', 'random']), 
              default='asc', help='Ordre de tri des fichiers.')
def search_command(directory: str, extension: str, delete: bool, confirm: bool, 
                 display: bool, sort_order: str) -> None:
    """
    Recherche et gère les fichiers par extension.
    
    Arguments:
    \b
    DIRECTORY  Le répertoire dans lequel rechercher
    EXTENSION  L'extension des fichiers à rechercher (sans le point)
    """
    directory_path = Path(directory)
    
    try:
        # Recherche des fichiers
        _, files = find_files_with_extension(directory_path, extension, sort_order)
        
        # Exécution des actions demandées
        if delete:
            delete_files(directory_path, files, confirm)
        elif display:
            display_files_content(directory_path, files, confirm)
        else:
            # Par défaut, afficher simplement la liste des fichiers
            click.echo(f"\nFichiers avec l'extension '.{extension}' dans '{directory}':")
            for i, file in enumerate(files, 1):
                click.echo(f"{i}. {file}")
            
            click.echo(f"\nTotal: {len(files)} fichier(s)")
            click.echo("\nUtilisez les options --delete ou --display pour agir sur ces fichiers.")
    
    except click.BadParameter as e:
        click.echo(f"Erreur: {e}")
    except Exception as e:
        click.echo(f"Une erreur inattendue s'est produite: {e}")
        logger.error(f"Erreur inattendue: {e}", exc_info=True)


@cli.command('analyze')
@click.argument('directory', type=click.Path(exists=True))
def analyze_command(directory: str) -> None:
    """
    Analyse un répertoire et compte les fichiers par extension.
    
    Arguments:
    \b
    DIRECTORY  Le répertoire à analyser
    """
    directory_path = Path(directory)
    
    click.echo(f"Analyse du répertoire: {directory_path}")
    extensions = count_files_by_extension(directory_path)
    
    if not extensions:
        click.echo("Aucun fichier trouvé dans ce répertoire.")
        return
    
    # Tri des extensions par nombre de fichiers (décroissant)
    sorted_extensions = sorted(extensions.items(), key=lambda x: x[1], reverse=True)
    
    click.echo("\nFichiers par extension:")
    click.echo("─" * 30)
    for ext, count in sorted_extensions:
        click.echo(f"{ext:<10} : {count:>5} fichier(s)")
    
    total = sum(extensions.values())
    click.echo("─" * 30)
    click.echo(f"Total   : {total:>5} fichier(s)")


if __name__ == "__main__":
    cli()