import builtins
import logging
from os import error, name, read
from typing import NamedTuple
from venv import logger
from attr import dataclass, field
from click import File
from more_itertools import first
import numpy as np
from prometheus_client import h
from pyparsing import line
from fileIO import File


class ENVIfile(File):
    def __init__(self, filePath):
        super().__init__(filePath)
        self.hdr = ENVIhdr()
        self.data = EnviData()

@dataclass
class ENVIhdr():
    '''
    ENVI header file class
    ENVI header file is a text file that contains metadata information about the image data file.
    The required parameters are 8: bands, byteOrder, dataType, fileType, headerOffset, interleave, lines, samples.
    '''
    acquisitionTime: str = field(default=None)
    bandNames: str = field(default=None)
    bands: int = field(default=None, metadata={'description': 'Number of bands in the image', 'required': True})
    bbl: str = field(metadata={'description': 'Bad band list', 'required': False})
    byteOrder: str = field(metadata={'description': 'Byte order of the data', 'required': True})
    classLookup: str
    classNames: str
    classes: int
    cloudCover: str
    colorTable: str
    complexFunction: str
    coordinateSystemString: str
    dataGainValues: str
    dataIgnoreValue: str
    dataOffsetValues: str
    dataReflectanceGainValues: str
    dataReflectanceOffsetValues: str
    dataType: str = field(metadata={'description': 'Data type of the image', 'required': True}, validator=lambda x: x in ['1', '2', '3', '4', '5', '6', '9', '12', '13', '14', '15'])
    defaultBands: str
    defaultStretch: str
    demBand: str
    demFile: str
    description: str
    fileType: str = field(metadata={'description': 'Type of the file: ', 'required': True})
    fwhm: str
    geoPoints: str
    headerOffset: int = field(metadata={'description': 'Offset of the header', 'required': True})
    interleave: str = field(metadata={'description': 'Interleave format of the data', 'required': True}, validator=lambda x: x in ['BIL', 'BIP', 'BSQ'])
    lines: int = field(metadata={'description': 'Number of lines in the image', 'required': True})
    mapInfo: str
    pixelSize: str
    projectionInfo: str
    readProcedures: str
    reflectanceScaleFactor: str
    rpcInfo: str
    samples: int = field(metadata={'description': 'Number of samples(pixels) per image line for each band', 'required': True})
    securityTag: str
    sensorType: str
    solarIrradiance: str
    spectraNames: str
    sunAzimuth: str
    sunElevation: str
    timestamp: str
    wavelength: str = field(metadata={'description': 'Wavelength of the image'})
    wavelengthUnits: str = field(metadata={'description': 'Units of the wavelength'}, validator=lambda x: x in ['Micrometers', 'um', 'Nanometers', 'nm', 'Millimeters', 'mm', 'Centimeters', 'cm', 'Meters', 'm', 'Wavenumber', 'Angstroms', 'GHz', 'MHz', 'Index', 'Unknown'])
    xStart: str
    yStart: str
    zPlotAverage: str
    zPlotRange: str
    zPlotTitles: str








class ENVIhdrHandler():

    # __all_paramsInfo = NamedTuple("allParas", ["acquisition time", "band names", "bands", "bbl", "byte order", "class lookup", "class names", "classes", "cloud cover", "color table", "complex function", "coordinate system string", "data gain values", "data ignore value", "data offset values", "data reflectance gain values", "data reflectance offset values", "data type", "default bands", "default stretch", "dem band", "dem file", "description", "file type", "fwhm", "geo points", "header offset", "interleave", "lines", "map info", "pixel size", "projection info", "read procedures", "reflectance scale factor", "rpc info", "samples", "security tag", "sensor type", "solar irradiance", "spectra names", "sun azimuth", "sun elevation", "timestamp", "wavelength", "wavelength units", "x start", "y start", "z plot average", "z plot range", "z plot titles", ])

    __std_paramsInfo = NamedTuple("stdParas", ['description', 'samples', 'lines', 'bands', 'header offset', 'file type', 'data type', 'interleave', 'sensor type', 'byte order', 'reflectance scale factor','map info'])

    __req_paramsInfo = NamedTuple("reqParas", "bands, byteOrder, dataType, fileType, headerOffset, interleave, lines, samples")

    def __init__(self):

        self.stdParas = None
        self.reqParas = None
    
    @property
    def hdr_dict(self):
        if self.hdr_dict is None:
            self.hdr_dict = self.read()
        return self.hdr_dict
    
    @staticmethod
    def read(self, file) -> dict:
        '''
        USAGE: hdr = read_envi_header(file)
        Reads an ENVI ".hdr" file header and returns the parameters in a
        dictionary as strings.  Header field names are treated as case
        insensitive and all keys in the dictionary are lowercase.
        '''
        with open(file, 'r') as f:
            try:
                firstLine = f.readline().strip().startswith('ENVI')
            except Exception as e:
                logger.error(f'File does not appear to be an ENVI header (appears to be a binary file).\n{e}')
            else:
                if not firstLine:
                    logger.error = 'File does not appear to be an ENVI header (missing "ENVI" at beginning of first line).'

            lines = f.readlines()
            dict = {}
            try:
                while lines:
                    line = lines.pop(0)
                    if line.find('=') == -1: continue
                    if line[0] == ';': continue

                    (key, sep, val) = line.partition('=')
                    key = key.strip()
                    if not key.islower():
                        key = key.lower()
                    val = val.strip()
                    if val and val[0] == '{':
                        str = val.strip()
                        while str[-1] != '}':
                            line = lines.pop(0)
                            if line[0] == ';': continue
                            str += '\n' + line.strip()
                        if key == 'description':
                            dict[key] = str.strip('{}').strip()
                        else:
                            vals = str[1:-1].split(',')
                            for j in range(len(vals)):
                                vals[j] = vals[j].strip()
                            dict[key] = vals
                    else:
                        dict[key] = val
                return dict
            except Exception as e:
                logger.error(f'Error reading ENVI header file.\n{e}')
    
    def write(self, fileName, is_library= False):

        fout = builtins.open(fileName, 'w')
        d = {}
        d.update(header_dict)

        if is_library:
            d['file type'] = 'ENVI Spectral Library'
        elif 'file type' not in d:
            d['file type'] = 'ENVI Standard'
        fout.write('ENVI\n')

        # Write the standard parameters at the top of the file
        std_params = self.std_params
        for k in std_params:
            if k in d:
                _write_header_param(fout, k, d[k])
        for k in d:
            if k not in std_params:
                _write_header_param(fout, k, d[k])
        fout.close()

        pass

    def update(self):
        pass

        return headr_dict

class EnviData():
    def __init__(self):
        self.exts= ['img', 'dat', 'sli', 'hyspex', 'raw']
        self.dtype= [('1', np.uint8),                       # unsigned byte
                     ('2', np.int16),                       # 16-bit int
                     ('3', np.int32),                       # 32-bit int
                     ('4', np.float32),                     # 32-bit float
                     ('5', np.float64),                     # 64-bit float
                     ('6', np.complex64),                   # 2x32-bit complex
                     ('9', np.complex128),                  # 2x64-bit complex
                     ('12', np.uint16),                     # 16-bit unsigned int
                     ('13', np.uint32),                     # 32-bit unsigned int
                     ('14', np.int64),                      # 64-bit int
                     ('15', np.uint64)]                     # 64-bit unsigned int
        
        self.envi_to_dtype = {'1': 'uint8', '2': 'int16', '3': 'int32',
                              '4': 'float32', '5': 'float64', '6': 'complex64',
                              '9': 'complex128', '12': 'uint16', '13': 'uint32',
                              '14': 'int64', '15': 'uint64'}
    
    def get_params(self):
        '''
        Parse an envi_header to a `Params` object.
        Arguments:
        `envi_header` (dict or file_name):
            A dict or an `.hdr` file name
        '''
        if not isinstance(envi_header, dict):
            headerPath = find_file_path(envi_header)
            h = read_envi_header(headerPath)
        else:
            h = envi_header

        class Params:
            pass
        p = Params()
        p.nbands = int(h["bands"])
        p.nrows = int(h["lines"])
        p.ncols = int(h["samples"])
        p.offset = int(h["header offset"]) if "header offset" in h else int(0)
        p.byte_order = int(h["byte order"])
        p.dtype = np.dtype(envi_to_dtype[str(h["data type"])]).str
        if p.byte_order != spy.byte_order:
            p.dtype = np.dtype(p.dtype).newbyteorder().str
        p.filename = None
        return p
    
    def open(self, file, image=None):
        '''
        Opens an image or spectral library with an associated ENVI HDR header file.
        Arguments:
            `file` (str):
                Name of the header file for the image.
            `image` (str):
                Optional name of the associated image data file.
        Returns:
            :class:`spectral.SpyFile` or :class:`spectral.io.envi.SpectralLibrary`
            object.
        Raises:
            TypeError, EnviDataFileNotFoundError
        If the specified file is not found in the current directory, all directories listed in the SPECTRAL_DATA environment variable will be searched until the file is found.  Based on the name of the header file, this function will search for the image file in the same directory as the header, looking for a file with the same name as the header but different extension. Extensions recognized are .img, .dat, .sli, and no extension. Capitalized versions of the file extensions are also searched.
        '''

        header_path = find_file_path(file)
        h = read_envi_header(header_path)
        check_compatibility(h)
        p = gen_params(h)

        inter = h["interleave"]

        #  Validate image file name
        if not image:
            #  Try to determine the name of the image file
            (header_path_title, header_ext) = os.path.splitext(header_path)
            if header_ext.lower() == '.hdr':
                exts = [ext.lower() for ext in KNOWN_EXTS] + [inter.lower()]
                exts = [''] + exts + [ext.upper() for ext in exts]
                for ext in exts:
                    if len(ext) == 0:
                        testname = header_path_title
                    else:
                        testname = header_path_title + '.' + ext
                    if os.path.isfile(testname):
                        image = testname
                        break
            if not image:
                msg = 'Unable to determine the ENVI data file name for the ' \
                'given header file. You can specify the data file by passing ' \
                'its name as the optional `image` argument to envi.open.'
                raise EnviDataFileNotFoundError(msg)
        else:
            image = find_file_path(image)

        p.filename = image

        if h.get('file type') == 'ENVI Spectral Library':
            # File is a spectral library
            data = np.fromfile(p.filename, p.dtype, p.ncols * p.nrows)
            data.shape = (p.nrows, p.ncols)
            return SpectralLibrary(data, h, p)

        #  Create the appropriate object type for the interleave format.
        inter = h["interleave"]
        if inter == 'bil' or inter == 'BIL':
            img = BilFile(p, h)
        elif inter == 'bip' or inter == 'BIP':
            img = BipFile(p, h)
        else:
            img = BsqFile(p, h)

        img.scale_factor = float(h.get('reflectance scale factor', 1.0))

        # Add band info

        if 'wavelength' in h:
            try:
                img.bands.centers = [float(b) for b in h['wavelength']]
            except:
                pass
        if 'fwhm' in h:
            try:
                img.bands.bandwidths = [float(f) for f in h['fwhm']]
            except:
                pass
        img.bands.band_unit = h.get('wavelength units', None)

        if 'bbl' in h:
            try:
                h['bbl'] = [int(float(b)) for b in h['bbl']]
            except:
                logger.warning('Unable to parse bad band list (bbl) in ENVI ' \
                            'header as integers.')
        return img


# define logger
logging.basicConfig(
    filename=os.path.join(os.path.dirname(__file__), '__testData__', 'asd_file_handle.log'),
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - Line: %(lineno)d'
)

logger = logging.getLogger(__name__)