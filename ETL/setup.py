import os
import subprocess
import sys
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Ana dizin - Movie-Recommendation-System ETL klasörü
base_dir = os.path.dirname(os.path.abspath(__file__))
script_path = os.path.join(base_dir, "find_content_imdb_id.py")

def run_scraper_instance(user_id):
    """Tek bir scraper instance'ını çalıştır"""
    try:
        print(f"\n🚀 User {user_id} için scraper başlatılıyor...")
        
        # find_content_imdb_id.py'yi user_id parametresi ile çalıştır
        result = subprocess.run(
            [sys.executable, script_path, str(user_id)],
            cwd=base_dir,
            capture_output=True,
            text=True,
            timeout=3600  # 1 saat timeout
        )
        
        if result.returncode == 0:
            print(f"✅ User {user_id} başarıyla tamamlandı")
            return user_id, True, result.stdout
        else:
            print(f"❌ User {user_id} hata ile sonlandı: {result.stderr}")
            return user_id, False, result.stderr
            
    except subprocess.TimeoutExpired:
        print(f"⏰ User {user_id} timeout oldu")
        return user_id, False, "Timeout"
    except Exception as e:
        print(f"💥 User {user_id} exception: {str(e)}")
        return user_id, False, str(e)

def run_scrapers_parallel(user_ids, max_workers=4):
    """Paralel olarak birden fazla scraper çalıştır"""
    print(f"\n🔄 {len(user_ids)} scraper paralel olarak başlatılıyor (max {max_workers} worker)...")
    
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Tüm task'ları submit et
        future_to_user = {executor.submit(run_scraper_instance, user_id): user_id 
                         for user_id in user_ids}
        
        # Sonuçları topla
        for future in as_completed(future_to_user):
            user_id = future_to_user[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as exc:
                print(f"💥 User {user_id} exception: {exc}")
                results.append((user_id, False, str(exc)))
    
    return results

def run_scrapers_sequential(user_ids):
    """Sıralı olarak scraper'ları çalıştır"""
    print(f"\n🔄 {len(user_ids)} scraper sıralı olarak başlatılıyor...")
    
    results = []
    for user_id in user_ids:
        result = run_scraper_instance(user_id)
        results.append(result)
        # Scraper'lar arası kısa bekleme
        time.sleep(1)
    
    return results

def main():
    """Ana fonksiyon"""
    print("🎬 IMDb Data Scraper Setup")
    print(f"📁 Çalışma dizini: {base_dir}")
    print(f"📄 Script yolu: {script_path}")
    
    # Script dosyasının varlığını kontrol et
    if not os.path.exists(script_path):
        print(f"❌ Script bulunamadı: {script_path}")
        sys.exit(1)
    
    # Kullanıcı ID'lerini belirle (0-15 arası)
    user_ids = list(range(16))
    
    # Çalıştırma modunu sor
    print("\n🔧 Çalıştırma modu seçin:")
    print("1. Paralel (hızlı, daha fazla kaynak kullanır)")
    print("2. Sıralı (yavaş, daha az kaynak kullanır)")
    print("3. Özel user ID'ler")
    
    try:
        choice = input("Seçiminiz (1/2/3): ").strip()
        
        if choice == "1":
            # Paralel çalıştırma
            max_workers = int(input("Maksimum paralel worker sayısı (önerilen: 4): ") or "4")
            results = run_scrapers_parallel(user_ids, max_workers)
            
        elif choice == "2":
            # Sıralı çalıştırma
            results = run_scrapers_sequential(user_ids)
            
        elif choice == "3":
            # Özel user ID'ler
            custom_ids = input("User ID'leri girin (virgülle ayırın, örn: 0,1,2): ")
            user_ids = [int(x.strip()) for x in custom_ids.split(",") if x.strip().isdigit()]
            
            if not user_ids:
                print("❌ Geçerli user ID bulunamadı")
                sys.exit(1)
                
            sub_choice = input("Paralel mi sıralı mı? (p/s): ").strip().lower()
            if sub_choice == "p":
                max_workers = int(input("Maksimum paralel worker sayısı: ") or "2")
                results = run_scrapers_parallel(user_ids, max_workers)
            else:
                results = run_scrapers_sequential(user_ids)
        else:
            print("❌ Geçersiz seçim")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️ İşlem kullanıcı tarafından durduruldu")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Hata: {e}")
        sys.exit(1)
    
    # Sonuçları özetle
    print("\n📊 SONUÇLAR:")
    successful = sum(1 for _, success, _ in results if success)
    failed = len(results) - successful
    
    print(f"✅ Başarılı: {successful}")
    print(f"❌ Başarısız: {failed}")
    print(f"📈 Başarı oranı: {successful/len(results)*100:.1f}%")
    
    # Başarısız olanları listele
    if failed > 0:
        print("\n❌ Başarısız user ID'ler:")
        for user_id, success, error in results:
            if not success:
                print(f"  User {user_id}: {error[:100]}...")
    
    print("\n🚀 Tüm işlemler tamamlandı!")

if __name__ == "__main__":
    main()

