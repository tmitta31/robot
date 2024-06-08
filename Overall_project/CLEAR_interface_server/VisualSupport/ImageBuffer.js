class ImageBuffer {

    constructor(buffer) {
        // Extract width and height from the first 8 bytes of the buffer
        this.width = buffer.readInt32LE(0);
        this.height = buffer.readInt32LE(4);

        // Initialize the matrix to hold the image pixels
        this.matrix = new Array(this.height).fill(null).map(() => new Array(this.width));

        // Fill the matrix with the pixel data
        let index = 8;
        for (let y = 0; y < this.height; y++) {
            for (let x = 0; x < this.width; x++) {
                const r = buffer[index++];
                const g = buffer[index++];
                const b = buffer[index++];
                this.matrix[y][x] = { r, g, b };
            }
        }
    }

    getPixel(x, y) {
        return this.matrix[y][x];
    }
}

module.exports = ImageBuffer;

// Usage:
// const imgData = Buffer.concat(chunks);
// const image = new ImageBuffer(imgData);
// const pixel = image.getPixel(10, 10);
// console.log(pixel);
