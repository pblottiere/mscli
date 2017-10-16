from cliff.command import Command
from owslib.wms import WebMapService
from melusine import settings


class Map(Command):

    def get_parser(self, prog_name):
        parser = super(Map, self).get_parser(prog_name)
        parser.add_argument('layers', nargs='*')
        parser.add_argument('--crs', nargs='?')
        parser.add_argument('--bbox', nargs='?')
        parser.add_argument('--transparent', nargs='?', default=True)
        parser.add_argument('--size', nargs='?')
        parser.add_argument('--format', nargs='?')
        parser.add_argument('--output', nargs='?')
        return parser

    def take_action(self, parsed_args):
        layers = parsed_args.layers
        server = settings.SERVER

        if not server:
            self.app.error('Not connected')
            return

        if not layers:
            self.app.error('At least 1 layer is necessary')
            return

        for l in layers:
            if l not in server.contents:
                self.app.error('Invalid layer \'{}\''.format(l))

        default_layer = server[layers[0]]
        bbox = parsed_args.bbox
        crs = parsed_args.crs

        if not crs:
            crs = default_layer.boundingBox[4]

        if not bbox:
            bbox = (default_layer.boundingBox[1],
                    default_layer.boundingBox[0],
                    default_layer.boundingBox[3],
                    default_layer.boundingBox[2])

        size = parsed_args.size
        if not size:
            size=(400,400)

        format = parsed_args.format
        if not format:
            format='image/jpeg'

        output = parsed_args.output
        if not output:
            output = '/tmp/melusine.jpeg'

        self.app.write('GetMap request parameters\n')
        self.app.write('  output        {}'.format(output) )

        img = server.getmap( layers=layers,
                             srs=crs,
                             bbox=bbox,
                             size=size,
                             format=format,
                             styles = [''],
                             transparent=True)

        out = open(output, 'wb')
        out.write(img.read())
        out.close()


class Disconnect(Command):

    def take_action(self, parsed_args):
        settings.SERVER = None
        self.app.success()