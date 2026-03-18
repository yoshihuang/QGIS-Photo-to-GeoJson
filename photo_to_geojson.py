import os
from PyQt6.QtWidgets import (QFileDialog, QMessageBox, QDialog, 
                             QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, 
                             QProgressBar, QApplication)
from PyQt6.QtCore import QSettings, QMetaType
from PyQt6.QtGui import QColor, QAction
from qgis.core import (QgsProject, QgsVectorLayer, QgsFeature, 
                       QgsGeometry, QgsPointXY, QgsFields, QgsField,
                       QgsVectorFileWriter, QgsSimpleMarkerSymbolLayer, 
                       QgsMarkerSymbol, QgsSingleSymbolRenderer, QgsProperty,
                       QgsSymbolLayer, QgsEditorWidgetSetup)
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

# ==========================================
# 1. Lightweight Multilingual Dictionary (i18n)
# ==========================================
I18N = {
    'en': {
        'plugin_name': 'Photo to GeoJSON',
        'dialog_title': 'Photo to GeoJSON Converter',
        'folder_placeholder': 'Select folder containing photos...',
        'output_placeholder': 'Set output GeoJSON file path...',
        'btn_browse': 'Browse',
        'btn_start': 'Start Conversion',
        'warn_title': 'Warning',
        'warn_msg': 'Please select both an input folder and an output path!',
        'info_title': 'Information',
        'info_no_photos': 'No supported photos found in the selected folder.',
        'dialog_folder': 'Select Photo Folder',
        'dialog_save': 'Save GeoJSON',
        'log_total': 'Total Processed: {}',
        'log_success': 'Success: {}',
        'log_fail': 'Failed: {}',
        'log_fail_list': '=== Failed List ===',
        'err_coord': '{}: Coordinate conversion error ({})',
        'err_nogps': '{}: No GPS info',
        'err_direction': '{}: Failed to extract image direction',
        'msg_done_title': 'Process Completed',
        'msg_done': 'Total: {}\nSuccess: {}\nFailed: {}\n\nLog saved to:\n{}'
    },
    'zh': {
        'plugin_name': '照片轉 GeoJSON',
        'dialog_title': '照片轉 GeoJSON 處理器',
        'folder_placeholder': '選擇包含照片的資料夾...',
        'output_placeholder': '設定輸出的 GeoJSON 檔案路徑...',
        'btn_browse': '瀏覽',
        'btn_start': '開始轉換',
        'warn_title': '警告',
        'warn_msg': '請確認已選擇輸入資料夾與輸出路徑！',
        'info_title': '提示',
        'info_no_photos': '資料夾內沒有找到支援的照片格式。',
        'dialog_folder': '選擇照片資料夾',
        'dialog_save': '儲存 GeoJSON',
        'log_total': '處理總數: {} 張',
        'log_success': '成功轉檔: {} 張',
        'log_fail': '失敗數量: {} 張',
        'log_fail_list': '=== 未轉檔成功清單 ===',
        'err_coord': '{}: 坐標轉換錯誤 ({})',
        'err_nogps': '{}: 無 GPS 資訊',
        'err_direction': '{}: 提取照片方向角失敗',
        'msg_done_title': '處理完成',
        'msg_done': '總計: {} 張\n成功: {} 張\n失敗: {} 張\n\n轉換日誌已儲存於:\n{}'
    },
    'ja': {
        'plugin_name': '写真から GeoJSON',
        'dialog_title': '写真から GeoJSON コンバーター',
        'folder_placeholder': '写真が含まれるフォルダを選択...',
        'output_placeholder': '出力する GeoJSON ファイルのパスを設定...',
        'btn_browse': '参照',
        'btn_start': '変換開始',
        'warn_title': '警告',
        'warn_msg': '入力フォルダと出力パスの両方を選択してください！',
        'info_title': '情報',
        'info_no_photos': '選択したフォルダにサポートされている写真が見つかりません。',
        'dialog_folder': '写真フォルダの選択',
        'dialog_save': 'GeoJSON を保存',
        'log_total': '処理総数: {}',
        'log_success': '成功: {}',
        'log_fail': '失敗: {}',
        'log_fail_list': '=== 失敗リスト ===',
        'err_coord': '{}: 座標変換エラー ({})',
        'err_nogps': '{}: GPS 情報なし',
        'err_direction': '{}: 画像の方向の抽出に失敗しました',
        'msg_done_title': '処理完了',
        'msg_done': '合計: {}\n成功: {}\n失敗: {}\n\nログ保存先:\n{}'
    },
    'ko': {
        'plugin_name': '사진을 GeoJSON으로',
        'dialog_title': '사진 변환기 (GeoJSON)',
        'folder_placeholder': '사진이 있는 폴더 선택...',
        'output_placeholder': '출력할 GeoJSON 파일 경로 설정...',
        'btn_browse': '찾아보기',
        'btn_start': '변환 시작',
        'warn_title': '경고',
        'warn_msg': '입력 폴더와 출력 경로를 모두 선택해주세요!',
        'info_title': '정보',
        'info_no_photos': '선택한 폴더에서 지원되는 사진을 찾을 수 없습니다.',
        'dialog_folder': '사진 폴더 선택',
        'dialog_save': 'GeoJSON 저장',
        'log_total': '총 처리 수: {}',
        'log_success': '성공: {}',
        'log_fail': '실패: {}',
        'log_fail_list': '=== 실패 목록 ===',
        'err_coord': '{}: 좌표 변환 오류 ({})',
        'err_nogps': '{}: GPS 정보 없음',
        'err_direction': '{}: 이미지 방향을 추출하지 못했습니다',
        'msg_done_title': '처리 완료',
        'msg_done': '총합: {}\n성공: {}\n실패: {}\n\n로그 저장 위치:\n{}'
    },
    'fr': {
        'plugin_name': 'Photo vers GeoJSON',
        'dialog_title': 'Convertisseur Photo vers GeoJSON',
        'folder_placeholder': 'Sélectionner le dossier contenant les photos...',
        'output_placeholder': 'Définir le chemin du fichier GeoJSON de sortie...',
        'btn_browse': 'Parcourir',
        'btn_start': 'Démarrer la conversion',
        'warn_title': 'Avertissement',
        'warn_msg': 'Veuillez sélectionner un dossier source et un chemin de destination !',
        'info_title': 'Information',
        'info_no_photos': 'Aucune photo prise en charge trouvée dans le dossier selected.',
        'dialog_folder': 'Sélectionner le dossier de photos',
        'dialog_save': 'Enregistrer GeoJSON',
        'log_total': 'Total traité : {}',
        'log_success': 'Succès : {}',
        'log_fail': 'Échec : {}',
        'log_fail_list': '=== Liste des échecs ===',
        'err_coord': '{}: Erreur de conversion des coordonnées ({})',
        'err_nogps': '{}: Aucune info GPS',
        'err_direction': '{}: Échec de l\'extraction de la direction de l\'image',
        'msg_done_title': 'Traitement terminé',
        'msg_done': 'Total : {}\nSuccès : {}\nÉchec : {}\n\nJournal enregistré dans :\n{}'
    },
    'es': {
        'plugin_name': 'Foto a GeoJSON',
        'dialog_title': 'Convertidor de Foto a GeoJSON',
        'folder_placeholder': 'Seleccionar carpeta con fotos...',
        'output_placeholder': 'Establecer ruta del archivo GeoJSON de salida...',
        'btn_browse': 'Examinar',
        'btn_start': 'Iniciar Conversión',
        'warn_title': 'Advertencia',
        'warn_msg': '¡Por favor, seleccione una carpeta de entrada y una ruta de salida!',
        'info_title': 'Information',
        'info_no_photos': 'No se encontraron fotos compatibles en la carpeta.',
        'dialog_folder': 'Seleccionar carpeta de fotos',
        'dialog_save': 'Guardar GeoJSON',
        'log_total': 'Total procesado: {}',
        'log_success': 'Éxito: {}',
        'log_fail': 'Fallo: {}',
        'log_fail_list': '=== Lista de fallos ===',
        'err_coord': '{}: Error de conversion de coordenadas ({})',
        'err_nogps': '{}: Sin información GPS',
        'err_direction': '{}: Fallo al extraer la dirección de la imagen',
        'msg_done_title': 'Proceso completado',
        'msg_done': 'Total: {}\nÉxito: {}\nFallo: {}\n\nRegistro guardado en:\n{}'
    }
}

# ==========================================
# 2. Locale Detection and Translation Function
# ==========================================
def get_translator():
    user_locale = QSettings().value("locale/userLocale", "en_US")
    lang_code = str(user_locale)[0:2].lower()
    current_lang = I18N.get(lang_code, I18N['en'])
    
    def tr(key, *args):
        text = current_lang.get(key, I18N['en'].get(key, key))
        return text.format(*args) if args else text
    return tr

tr = get_translator()

# ==========================================
# 3. Main Plugin Class and UI Interface
# ==========================================
class PhotoToGeoJSONPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.action = None

    def initGui(self):
        self.action = QAction(tr('plugin_name'), self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addPluginToMenu(tr('plugin_name'), self.action)

    def unload(self):
        self.iface.removePluginMenu(tr('plugin_name'), self.action)

    def run(self):
        self.dialog = PluginDialog(self.iface.mainWindow())
        self.dialog.show()

class PluginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr('dialog_title'))
        self.resize(400, 200)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        folder_layout = QHBoxLayout()
        self.folder_input = QLineEdit()
        self.folder_input.setPlaceholderText(tr('folder_placeholder'))
        btn_folder = QPushButton(tr('btn_browse'))
        btn_folder.clicked.connect(self.select_folder)
        folder_layout.addWidget(self.folder_input)
        folder_layout.addWidget(btn_folder)
        layout.addLayout(folder_layout)

        output_layout = QHBoxLayout()
        self.output_input = QLineEdit()
        self.output_input.setPlaceholderText(tr('output_placeholder'))
        btn_output = QPushButton(tr('btn_browse'))
        btn_output.clicked.connect(self.select_output)
        output_layout.addWidget(self.output_input)
        output_layout.addWidget(btn_output)
        layout.addLayout(output_layout)

        self.progress = QProgressBar()
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        self.btn_run = QPushButton(tr('btn_start'))
        self.btn_run.clicked.connect(self.process_photos)
        layout.addWidget(self.btn_run)

        self.setLayout(layout)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, tr('dialog_folder'))
        if folder:
            self.folder_input.setText(folder)

    def select_output(self):
        file, _ = QFileDialog.getSaveFileName(self, tr('dialog_save'), "", "GeoJSON Files (*.geojson)")
        if file:
            self.output_input.setText(file)

    def get_exif_gps_azimuth(self, image_path):
        try:
            image = Image.open(image_path)
            exif_data = image._getexif()
            if not exif_data:
                return None, None
            
            decoded = {TAGS.get(tag, tag): value for tag, value in exif_data.items()}
            gps_info = {}
            if 'GPSInfo' in decoded:
                for t, v in decoded['GPSInfo'].items():
                    gps_info[GPSTAGS.get(t, t)] = v
            
            return decoded, gps_info
        except Exception:
            return None, None

    def convert_to_deg(self, value):
        d = float(value[0])
        m = float(value[1])
        s = float(value[2])
        return d + (m / 60.0) + (s / 3600.0)

    def convert_azimuth(self, value):
        try:
            if isinstance(value, tuple) and len(value) == 2:
                return float(value[0]) / float(value[1])
            return float(value)
        except (ValueError, TypeError, ZeroDivisionError):
            return 0.0

    def process_photos(self):
        input_folder = self.folder_input.text()
        output_file = self.output_input.text()

        if not input_folder or not output_file:
            QMessageBox.warning(self, tr('warn_title'), tr('warn_msg'))
            return

        self.btn_run.setEnabled(False)
        photo_files = [f for f in os.listdir(input_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.tif'))]
        total_photos = len(photo_files)
        
        if total_photos == 0:
            QMessageBox.information(self, tr('info_title'), tr('info_no_photos'))
            self.btn_run.setEnabled(True)
            return

        self.progress.setMaximum(total_photos)
        success_count = 0
        fail_files = []

        layer = QgsVectorLayer("Point?crs=epsg:4326", "Photos", "memory")
        provider = layer.dataProvider()
        provider.addAttributes([
            QgsField("FileName", QMetaType.Type.QString),
            QgsField("DateTime", QMetaType.Type.QString),
            QgsField("CameraMake", QMetaType.Type.QString),
            QgsField("Azimuth", QMetaType.Type.Double),
            QgsField("Longitude", QMetaType.Type.Double),
            QgsField("Latitude", QMetaType.Type.Double),
            QgsField("FullPath", QMetaType.Type.QString)
        ])
        layer.updateFields()

        features = []

        # Processing loop
        for i, filename in enumerate(photo_files):
            # Get the original absolute file path of the photo
            path = os.path.join(input_folder, filename)
            # Normalize slash direction and forcefully add the file:/// prefix
            full_path_url = 'file:///' + os.path.normpath(path).replace('\\', '/')
            
            exif, gps = self.get_exif_gps_azimuth(path)

            if gps and 'GPSLatitude' in gps and 'GPSLongitude' in gps:
                try:
                    # Calculate coordinates
                    lat = self.convert_to_deg(gps['GPSLatitude'])
                    lon = self.convert_to_deg(gps['GPSLongitude'])
                    if gps.get('GPSLatitudeRef') == 'S': lat = -lat
                    if gps.get('GPSLongitudeRef') == 'W': lon = -lon

                    # Extract azimuth (image direction)
                    azimuth = 0.0
                    if 'GPSImgDirection' in gps:
                        azimuth = self.convert_azimuth(gps['GPSImgDirection'])
                    elif exif and 'ImageDirection' in exif:
                        azimuth = self.convert_azimuth(exif['ImageDirection'])

                    # Create feature and populate all attributes
                    fet = QgsFeature(layer.fields())
                    fet.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(lon, lat)))
                    
                    attributes = [
                        filename, 
                        exif.get('DateTime', '') if exif else '', 
                        exif.get('Make', '') if exif else '', 
                        azimuth,
                        lon,
                        lat,
                        full_path_url
                    ]
                    
                    fet.setAttributes(attributes)
                    features.append(fet)
                    success_count += 1
                except Exception as e:
                    fail_files.append(tr('err_coord', filename, str(e)))
            else:
                fail_files.append(tr('err_nogps', filename))

            # Update progress bar and keep UI responsive
            self.progress.setValue(i + 1)
            QApplication.processEvents() 

        # Write features to the Memory Layer
        if features:
            provider.addFeatures(features)
            layer.updateExtents()
            
            # Save the Memory Layer as a GeoJSON file
            options = QgsVectorFileWriter.SaveVectorOptions()
            options.driverName = "GeoJSON"
            QgsVectorFileWriter.writeAsVectorFormatV3(layer, output_file, QgsProject.instance().transformContext(), options)

            # --- Load the GeoJSON file into the map ---
            geojson_layer = QgsVectorLayer(output_file, os.path.basename(output_file), "ogr")
            if geojson_layer.isValid():
                # 1. Set arrow symbol
                arrow_symbol_layer = QgsSimpleMarkerSymbolLayer()
                arrow_symbol_layer.setShape(QgsSimpleMarkerSymbolLayer.Arrow)
                arrow_symbol_layer.setSize(5.0) 
                arrow_symbol_layer.setColor(QColor(255, 0, 0, 255)) 
                arrow_symbol_layer.setStrokeColor(QColor(0, 0, 0, 255))

                # Create point symbol and apply the symbol layer
                point_symbol = QgsMarkerSymbol()
                point_symbol.changeSymbolLayer(0, arrow_symbol_layer)

                # Set symbol rotation property (bound to the "Azimuth" field)
                property_rot = QgsProperty.fromExpression("to_real(\"Azimuth\")")
                point_symbol.symbolLayer(0).setDataDefinedProperty(QgsSymbolLayer.PropertyAngle, property_rot)

                # Create a single symbol renderer and apply the symbol
                renderer = QgsSingleSymbolRenderer(point_symbol)
                geojson_layer.setRenderer(renderer)
                
                # ==========================================
                # Set up the Identify tool and Map Tip photo preview
                # ==========================================
                field_idx = geojson_layer.fields().indexOf("FullPath")
                if field_idx != -1:
                    setup = QgsEditorWidgetSetup('ExternalResource', {
                        'DocumentViewer': 1,       
                        'DocumentViewerWidth': 0,  
                        'DocumentViewerHeight': 300, 
                        'RelativeStorage': 0        
                    })
                    geojson_layer.setEditorWidgetSetup(field_idx, setup)

                # Configure Map Tip (hover preview)
                map_tip_html = """
                <div style="text-align:center;">
                  <b>[% "FileName" %]</b><br>
                  <img src="[% "FullPath" %]" width="300" /><br>
                  <span style="color:gray; font-size:small;">[% "DateTime" %]</span>
                </div>
                """
                geojson_layer.setMapTipTemplate(map_tip_html)
                # ==========================================

                # Add the configured layer to the map
                QgsProject.instance().addMapLayer(geojson_layer)
                geojson_layer.triggerRepaint()

        # Generate Log file
        log_path = os.path.splitext(output_file)[0] + "_log.txt"
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(tr('log_total', total_photos) + "\n")
            f.write(tr('log_success', success_count) + "\n")
            f.write(tr('log_fail', len(fail_files)) + "\n\n")
            f.write(tr('log_fail_list') + "\n")
            f.write("\n".join(fail_files))

        self.btn_run.setEnabled(True)
        QMessageBox.information(
            self, 
            tr('msg_done_title'), 
            tr('msg_done', total_photos, success_count, len(fail_files), log_path)
        )