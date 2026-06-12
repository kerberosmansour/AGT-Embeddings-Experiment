use std::fs::File;
use std::io::{BufWriter, Write};
use std::path::PathBuf;

use anyhow::Context;
use arrow_json::LineDelimitedWriter;
use clap::Parser;
use parquet::arrow::arrow_reader::ParquetRecordBatchReaderBuilder;

#[derive(Debug, Parser)]
#[command(
    name = "parquet-to-jsonl",
    about = "Convert a Parquet file to line-delimited JSON for corpus intake"
)]
struct Args {
    /// Input Parquet file.
    input: PathBuf,

    /// Output JSONL path. Defaults to stdout.
    #[arg(short, long)]
    output: Option<PathBuf>,

    /// Rows per Arrow record batch.
    #[arg(long, default_value_t = 8192)]
    batch_size: usize,

    /// Stop after this many rows.
    #[arg(long)]
    limit: Option<usize>,

    /// Print the converted Arrow schema and exit.
    #[arg(long)]
    schema: bool,
}

fn main() -> anyhow::Result<()> {
    let args = Args::parse();
    if args.batch_size == 0 {
        anyhow::bail!("--batch-size must be greater than zero");
    }

    let input = File::open(&args.input)
        .with_context(|| format!("failed to open {}", args.input.display()))?;
    let builder = ParquetRecordBatchReaderBuilder::try_new(input).with_context(|| {
        format!(
            "failed to read Parquet metadata from {}",
            args.input.display()
        )
    })?;

    if args.schema {
        println!("{}", builder.schema());
        return Ok(());
    }

    let reader = builder.with_batch_size(args.batch_size).build()?;
    let output: Box<dyn Write> = match &args.output {
        Some(path) => Box::new(
            File::create(path).with_context(|| format!("failed to create {}", path.display()))?,
        ),
        None => Box::new(std::io::stdout()),
    };
    let mut writer = LineDelimitedWriter::new(BufWriter::new(output));
    let mut written = 0usize;

    for batch in reader {
        let batch = batch?;
        let batch = if let Some(limit) = args.limit {
            if written >= limit {
                break;
            }
            let remaining = limit - written;
            if batch.num_rows() > remaining {
                batch.slice(0, remaining)
            } else {
                batch
            }
        } else {
            batch
        };

        written += batch.num_rows();
        writer.write_batches(&[&batch])?;
    }

    writer.finish()?;
    Ok(())
}
