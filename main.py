#!/usr/bin/env python3
import click
from src.pipeline import TTSPipeline
from adapters.google_adapters.google_tts_adapter import GoogleVoicePresets
import os
from pathlib import Path


def get_available_chirp3_presets():
    """Get list of available Chirp 3 voice presets"""
    presets = []
    for name in dir(GoogleVoicePresets):
        if not name.startswith("_") and callable(getattr(GoogleVoicePresets, name)):
            try:
                config = getattr(GoogleVoicePresets, name)()
                if "chirp3" in config.voice_name.lower():
                    presets.append(name)
            except:
                pass
    return presets


@click.command()
@click.argument("docx_file", type=click.Path(exists=True))
@click.option(
    "--output-name",
    "-o",
    default="interview_dialogue",
    help="Output filename (without extension)",
)


# Then in the Click option:
@click.option(
    "--voice",
    "-v",
    default="professional_female",
    type=click.Choice(get_available_chirp3_presets()),
    help="Voice preset to use",
)
@click.option(
    "--batch", "-b", is_flag=True, help="Create separate files for each Q&A pair"
)
@click.option(
    "--region", "-r", default="global", help="Google Cloud region for TTS service"
)
@click.option(
    "--service",
    "-s",
    default="google",
    type=click.Choice(["google"]),
    help="TTS service provider",
)
def main(docx_file, output_name, voice, batch, region, service):
    """
    Convert Q&A from DOCX file to high-quality speech audio using Google Chirp 3

    DOCX_FILE: Path to the Word document containing Q&A content

    Examples:
        python main.py interview_questions.docx
        python main.py questions.docx --voice confident_male --batch
        python main.py prep.docx -o leadership_prep -v professional_female
    """

    # Validate voice preset exists
    if not hasattr(GoogleVoicePresets, voice):
        click.echo(f"❌ Error: Voice preset '{voice}' not found")
        click.echo(f"Available presets: {', '.join(get_available_chirp3_presets())}")
        return

    # Convert relative path to absolute if needed
    docx_path = Path(docx_file).resolve()

    try:
        # Initialize pipeline
        click.echo(f"🔧 Initializing {service.upper()} TTS pipeline...")
        pipeline = TTSPipeline(service=service, server_region=region)

        # Process document
        click.echo(f"📄 Processing document: {docx_path.name}")
        click.echo(f"🎙️  Using voice: {voice}")
        click.echo(f"🌍 Region: {region}")

        if batch:
            click.echo("📦 Batch mode: Creating separate files for each Q&A pair")
        else:
            click.echo("📄 Single mode: Creating one combined audio file")

        result = pipeline.process_document(
            docx_path=str(docx_path),
            output_name=output_name,
            voice_preset=voice,
            batch_mode=batch,
        )

        # Display results
        if batch:
            click.echo(f"✅ Successfully created {len(result)} audio files:")
            for i, file_path in enumerate(result[:5], 1):  # Show first 5
                click.echo(f"   {i}. {Path(file_path).name}")
            if len(result) > 5:
                click.echo(f"   ... and {len(result) - 5} more files")
            click.echo(f"📁 Output directory: {Path(result[0]).parent}")
        else:
            click.echo(f"✅ Audio file created: {Path(result).name}")
            click.echo(f"📁 Full path: {result}")

            # Show file size
            file_size_mb = Path(result).stat().st_size / (1024 * 1024)
            click.echo(f"📊 File size: {file_size_mb:.1f} MB")

    except FileNotFoundError as e:
        click.echo(f"❌ File not found: {e}")
        click.echo("💡 Make sure the DOCX file path is correct")

    except ValueError as e:
        if "credentials" in str(e).lower():
            click.echo("❌ Google Cloud credentials not found!")
            click.echo("💡 Setup steps:")
            click.echo("   1. Create Google Cloud project")
            click.echo("   2. Enable Text-to-Speech API")
            click.echo("   3. Create service account and download JSON key")
            click.echo("   4. Set GOOGLE_APPLICATION_CREDENTIALS in .env file")
        elif "Q&A pairs" in str(e):
            click.echo("❌ No Q&A content found in document!")
            click.echo("💡 Supported formats:")
            click.echo("   • Q: Question text A: Answer text")
            click.echo("   • Question: ... Answer: ...")
            click.echo("   • 1. Question text Answer: ...")
        else:
            click.echo(f"❌ Error: {e}")

    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}")
        click.echo("💡 Please check your document format and try again")


@click.command()
@click.option(
    "--service", "-s", default="google", help="TTS service to list voices for"
)
def list_voices(service):
    """List available voices for the TTS service"""
    try:
        if service == "google":
            from adapters.google_adapters.google_tts_adapter import (
                GoogleTTSModelHandler,
            )

            click.echo("🔧 Initializing Google TTS...")
            handler = GoogleTTSModelHandler()

            click.echo("🎙️  Available Google Chirp 3 voices:")
            voices = handler.get_available_voices()

            chirp_voices = [v for v in voices if "chirp3" in v["name"].lower()]

            for voice in chirp_voices:
                click.echo(
                    f"   • {voice['name']} (Sample rate: {voice['natural_sample_rate']} Hz)"
                )

            if not chirp_voices:
                click.echo("   No Chirp 3 voices found. Showing all voices:")
                for voice in voices[:10]:  # Show first 10
                    click.echo(f"   • {voice['name']}")

    except Exception as e:
        click.echo(f"❌ Error listing voices: {e}")


# Create CLI group
@click.group()
def cli():
    """Text-to-Speech Pipeline for Interview Preparation"""
    pass


# Add commands to group
cli.add_command(main, name="convert")
cli.add_command(list_voices, name="voices")

if __name__ == "__main__":
    # If called directly, run the main convert command
    import sys

    if len(sys.argv) == 1:
        click.echo("📚 TTS Pipeline - Text to Speech for Interview Prep")
        click.echo("Usage: python main.py [DOCX_FILE] [OPTIONS]")
        click.echo("       python main.py --help")
        click.echo("\nQuick start:")
        click.echo("  python main.py questions.docx")
        click.echo("  python main.py questions.docx --voice confident_male --batch")
    else:
        # Check if first argument looks like a command
        if sys.argv[1] in ["convert", "voices", "--help", "-h"]:
            cli()
        else:
            # Assume it's a direct file call, run convert command
            main()
