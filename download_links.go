package main

// I am writing this program to print a list of web pages to PDF so I can push them to EInk Tablet.

import (
	"bufio"
	"path/filepath"
	"fmt"
	"math/rand"
	"net/url"
	"os"
	s "strings"
	"time"
	pdf "github.com/SebastiaanKlippert/go-wkhtmltopdf"
)

func check(e error) {
	if e != nil {
		panic(e)
	}
}

type webpage struct {
	url      string
	filename string
}

func main() {
	// Initial setup
	linksFile, outDir := parseParameters()
	ensureDirectory(outDir)

	fmt.Println("Reading links from", linksFile,
		"\nDownloading into", outDir,
	)

	// ToDo: Need to run xvfb and tell go-wkhtmltopdf about it

	// Create new PDF generator
	pdfg, err := pdf.NewPDFGenerator()
	check(err)

	// Create a new input page from an URL
	page := pdf.NewPage("https://godoc.org/github.com/SebastiaanKlippert/go-wkhtmltopdf")

	pdfg.AddPage(page)

	// Create PDF document in internal buffer
	err = pdfg.Create()
	check(err)

	// Write buffer contents to file on disk
	err = pdfg.WriteFile("./simplesample.pdf")
	check(err)

	// Read links from file
	linksChan := startReadingLinks(linksFile)

	for s := range linksChan {
		fmt.Println(s)
	}
}

func randomInt(n int) int {
	seed := rand.NewSource(200 * time.Now().UnixNano())
	random_generator := rand.New(seed)
	return random_generator.Intn(n)
}

func parseParameters() (linksFile string, outDir string) {
	// Links file
	if len(os.Args) < 2 {
		fmt.Println("Please provide a file of \\n separated links")
		os.Exit(1)
	}
	linksFile = os.Args[1]

	// Output directory
	if len(os.Args) < 3 {
		outDir = fmt.Sprintf(
			"PDF_Download_%s_%d",
			time.Now().Format("2006-Jan-2"),
			randomInt(1000),
		)
	} else {
		outDir = os.Args[2]
	}
	return
}

func ensureDirectory(outDir string) {
	_, err := os.Stat(outDir)
	if os.IsNotExist(err) {
		os.Mkdir(outDir, 0700)
	} else if err != nil {
		panic(err)
	}
	return
}

func startReadingLinks(linksFile string) (linksChan chan webpage) {
	// Channel for reading from file, buffered to 10 lines
	linksChan = make(chan webpage, 10)

	file, err := os.Open(linksFile)
	check(err)

	go func() {
		defer file.Close()
		defer close(linksChan)

		scanner := bufio.NewScanner(file)
		for scanner.Scan() {
			link := scanner.Text()
			u, err := url.Parse(link)
			check(err)

			filename := s.TrimSuffix(u.Path, filepath.Ext(u.Path))
			filename = s.TrimSuffix(filename, "/")
			filename = u.Host + filename + ".pdf"
			filename = s.Replace(filename, "/", "_", -1)
			
			linksChan <- webpage{
				url:      link,
				filename: filename,
			}
		}
	}()

	return
}
