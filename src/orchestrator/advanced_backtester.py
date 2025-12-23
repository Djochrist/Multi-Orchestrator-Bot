print("\nRésultats du backtesting:")
    print(results.to_string(index=False))

    # Sauvegarder les résultats
    results.to_csv('backtest_results_1year.csv', index=False)

    # Créer les graphiques
    try:
        backtester.plot_comparison(results, save_path='strategy_comparison_1year.png')
    except Exception as e:
        logger.error(f"Erreur lors de la création des graphiques: {e}")

    # Identifier la meilleure stratégie
    best_strategy = results.loc[results['Sharpe Ratio'].idxmax()]

    print("\n=== Résumé ===")
    print(f"Meilleure stratégie: {best_strategy['Strategy']}")
    print(f"Rendement total: {best_strategy['Total Return (%)']:.2f}%")
    print(f"Ratio Sharpe: {best_strategy['Sharpe Ratio']:.3f}")
    print(f"Max Drawdown: {best_strategy['Max Drawdown (%)']:.2f}%")
    print(f"Nombre de trades: {best_strategy['Total Trades']}")
    print(f"Win Rate: {best_strategy['Win Rate (%)']:.1f}%")


if __name__ == "__main__":
    main()
