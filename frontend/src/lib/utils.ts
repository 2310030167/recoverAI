/**
 * Formats monetary amounts in Indian Rupee format.
 * Examples: ₹80,000 | ₹1.24L | ₹8.42M
 */
export function formatINR(amount: number, compact: boolean = false): string {
  if (isNaN(amount) || amount === null || amount === undefined) {
    return '₹0.00';
  }

  const absAmount = Math.abs(amount);
  const sign = amount < 0 ? '-' : '';

  if (compact) {
    if (absAmount >= 10000000) { // 1 Crore = 10M
      return `${sign}₹${(absAmount / 10000000).toFixed(2)}Cr`;
    }
    if (absAmount >= 100000) { // 1 Lakh = 100k
      return `${sign}₹${(absAmount / 100000).toFixed(2)}L`;
    }
    if (absAmount >= 1000) {
      return `${sign}₹${(absAmount / 1000).toFixed(1)}k`;
    }
  }

  // Exact Indian Number Format
  const formatted = new Intl.NumberFormat('en-IN', {
    maximumFractionDigits: 2,
    minimumFractionDigits: 2
  }).format(absAmount);

  return `${sign}₹${formatted}`;
}

export function formatPercent(value: number): string {
  if (isNaN(value)) return '0.0%';
  return `${value.toFixed(1)}%`;
}

export function formatDate(dateString: string): string {
  try {
    const d = new Date(dateString);
    return d.toLocaleDateString('en-IN', {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    });
  } catch {
    return dateString;
  }
}
