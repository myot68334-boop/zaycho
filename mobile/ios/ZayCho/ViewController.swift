import UIKit
import WebKit

final class ViewController: UIViewController, WKNavigationDelegate {
    private lazy var appURL: URL = {
        let rawURL = Bundle.main.object(forInfoDictionaryKey: "AppBaseURL") as? String ?? "https://example.com"
        return URL(string: rawURL)!
    }()
    private let webView = WKWebView(frame: .zero, configuration: WKWebViewConfiguration())
    private let refreshControl = UIRefreshControl()
    private let activityIndicator = UIActivityIndicatorView(style: .large)

    override func loadView() {
        view = webView
    }

    override func viewDidLoad() {
        super.viewDidLoad()

        title = "Lyra Shop"
        view.backgroundColor = .systemBackground
        webView.navigationDelegate = self
        webView.allowsBackForwardNavigationGestures = true
        webView.scrollView.refreshControl = refreshControl
        refreshControl.addTarget(self, action: #selector(refreshPage), for: .valueChanged)

        navigationItem.rightBarButtonItem = UIBarButtonItem(
            barButtonSystemItem: .refresh,
            target: self,
            action: #selector(refreshPage)
        )

        activityIndicator.translatesAutoresizingMaskIntoConstraints = false
        activityIndicator.hidesWhenStopped = true
        view.addSubview(activityIndicator)
        NSLayoutConstraint.activate([
            activityIndicator.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            activityIndicator.centerYAnchor.constraint(equalTo: view.centerYAnchor)
        ])

        loadApp()
    }

    @objc private func refreshPage() {
        webView.reload()
    }

    private func loadApp() {
        activityIndicator.startAnimating()
        webView.load(URLRequest(url: appURL))
    }

    func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
        activityIndicator.stopAnimating()
        refreshControl.endRefreshing()
    }

    func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) {
        activityIndicator.stopAnimating()
        refreshControl.endRefreshing()
    }

    func webView(_ webView: WKWebView, didFailProvisionalNavigation navigation: WKNavigation!, withError error: Error) {
        activityIndicator.stopAnimating()
        refreshControl.endRefreshing()
    }
}
