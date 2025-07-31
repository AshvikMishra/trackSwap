import scrapper
import script
import cleaner

if __name__ == "__main__":
    print("🚀 Starting Amazon Music to Spotify Conversion...")

    print("\n📥 Running scraper...")
    scrapper.main()

    print("\n🧹 Running cleaner...")
    cleaner.main()

    print("\n🎧 Running Spotify uploader...")
    script.main()

    print("\n✅ Done!")