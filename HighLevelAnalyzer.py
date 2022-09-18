# High Level Analyzer
# For more information and documentation, please go to https://support.saleae.com/extensions/high-level-analyzer-extensions

from saleae.analyzers import HighLevelAnalyzer, AnalyzerFrame, StringSetting, NumberSetting, ChoicesSetting


# High level analyzers must subclass the HighLevelAnalyzer class.
class Hla(HighLevelAnalyzer):

    # 0 = NO FOLLOWING | 1 = READ | 2 = WRITE
    following_type = 0

    register_map = {
        0x00: "CONFIG",
        0x01: "EN_AA",
        0x02: "EN_RXADDR",
        0x03: "SETUP_AW",
        0x04: "SETUP_RETR",
        0x05: "REF_CH",
        0x06: "RF_SETUP",
        0x07: "STATUS",
        0x08: "OBSERVE_TX",
        0x09: "RPD",
        0x0A: "RX_ADDR_P0",
        0x0B: "RX_ADDR_P1",
        0x0C: "RX_ADDR_P2",
        0x0D: "RX_ADDR_P3",
        0x0E: "RX_ADDR_P4",
        0x0F: "RX_ADDR_P5",
        0x10: "TX_ADDR",
        0x11: "RX_PW_P0",
        0x12: "RX_PW_P1",
        0x13: "RX_PW_P2",
        0x14: "RX_PW_P3",
        0x15: "RX_PW_P4",
        0x16: "RX_PW_P5",
        0x17: "FIFO_STATUS",

        0x1C: "DYNPD",
        0x1D: "FEATURE"
    }



    # An optional list of types this analyzer produces, providing a way to customize the way frames are displayed in Logic 2.
    result_types = {
        'write_register': {
            'format': 'Write register {{data.register}}'
        },
        'read_register': {
            'format': 'Read register {{data.register}}'
        },
        'following': {
            'format': 'Register value: 0x{{data.value_hex}} {{data.value_bin}}'
        },
        'read_rx_payload': {
            'format': 'Read RX payload'
        },
        'write_tx_payload': {
            'format': 'Write TX payload'
        },
        'flush_tx': {
            'format': 'Flush TX FIFO'
        },
        'flush_rx': {
            'format': 'Flush RX FIFO'
        },
        'debug': {
            'format': 'Debug message: {{data.message}}'
        }
    }

    

    def __init__(self):
        '''
        Initialize HLA.

        Settings can be accessed using the same name used above.
        '''



    def decode(self, frame: AnalyzerFrame):
        '''
        Process a frame from the input analyzer, and optionally return a single `AnalyzerFrame` or a list of `AnalyzerFrame`s.

        The type and data values in `frame` will depend on the input analyzer.
        '''
        if (frame.type == "result"):
        
            mosi_bytes = frame.data["mosi"]
            mosi_int = int.from_bytes(mosi_bytes,"little")

            miso_bytes  = frame.data["miso"]
            miso_int = int.from_bytes(miso_bytes,"little")


            if (self.following_type == 1):
                self.following_type = 0
                return AnalyzerFrame('following', frame.start_time, frame.end_time, {'value_hex': format(miso_int,'02X'), 'value_bin': format(miso_int,'08b')})

            if (self.following_type == 2):
                self.following_type = 0
                
                return AnalyzerFrame('following', frame.start_time, frame.end_time, {'value_hex': format(mosi_int,'02X'), 'value_bin': format(mosi_int,'08b')})

            

            # Check which NRF24L01 command is being executed

            # Read Register R_REGISTER
            if ((mosi_int & 0b11100000) == 0b000000000):
                register_masked = mosi_int & 0b00011111
                register_name = self.register_map[register_masked]
                self.following_type = 1
                return AnalyzerFrame('read_register', frame.start_time, frame.end_time, {'register': register_name})

            # Write Register W_REGISTER
            if ((mosi_int & 0b11100000) == 0b00100000):
                register_masked = mosi_int & 0b00011111
                register_name = self.register_map[register_masked]
                self.following_type = 2
                return AnalyzerFrame('write_register', frame.start_time, frame.end_time, {'register': register_name})

            # Read RX-payload R_RX_PAYLOAD
            if (mosi_int == 0b01100001):
                return AnalyzerFrame('read_rx_payload', frame.start_time, frame.end_time)

            # Write TX-payload W_TX_PAYLOAD
            if (mosi_int == 0b10100000):
                return AnalyzerFrame('write_tx_payload', frame.start_time, frame.end_time)

            # Flush TX FIFO FLUSH_TX
            if (mosi_int == 0b11100001):
                return AnalyzerFrame('flush_tx', frame.start_time, frame.end_time)

            # Flush RX FIFO FLUSH_RX
            if (mosi_int == 0b11100010):
                return AnalyzerFrame('flush_rx', frame.start_time, frame.end_time)

            if ()