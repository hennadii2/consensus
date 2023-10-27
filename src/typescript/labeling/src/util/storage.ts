import { Storage } from "@google-cloud/storage";
import { parse } from "csv-parse";
import * as fs from "fs";
import { mkdir } from "node:fs/promises";
import * as Papa from "papaparse";
import * as path from "path";

interface GcloudServiceAuthJson {
  type: string;
  project_id: string;
  private_key_id: string;
  private_key: string;
  client_email: string;
  client_id: string;
  auth_uri: string;
  token_uri: string;
  auth_provider_x509_cert_url: string;
  client_x509_cert_url: string;
}

let storage: null | Storage = null;

/** Connects to GCS storage if not yet connected. */
export async function connectToStorage(): Promise<Storage> {
  if (storage === null) {
    const GCLOUD_AUTH_JSON = process.env.GCLOUD_AUTH_JSON;
    if (!GCLOUD_AUTH_JSON) {
      throw new Error("Missing process.env.GCLOUD_AUTH_JSON");
    }
    const auth: GcloudServiceAuthJson = JSON.parse(GCLOUD_AUTH_JSON);
    auth.private_key = auth.private_key.split(String.raw`\n`).join("\n");
    storage = new Storage({
      credentials: auth,
    });
  }
  return storage;
}

export interface StoragePath {
  bucket: string;
  path: string;
}

/** Parses a full GCS path into its bucket and file path components. */
export function getStoragePath(fullPath: string): StoragePath {
  const parts = fullPath.split("/");
  return {
    bucket: parts[0],
    path: parts.slice(1, parts.length).join("/"),
  };
}

/** Helper to return file basename from a StoragePath object. */
export function getBaseName(storagePath: StoragePath) {
  return path.basename(storagePath.path, path.extname(storagePath.path));
}

/** Returns a list of files stored at a GCS path. */
export async function listFiles(
  fullBucketPath: string
): Promise<StoragePath[]> {
  const storage = await connectToStorage();
  const storagePath = getStoragePath(fullBucketPath);
  const [files] = await storage.bucket(storagePath.bucket).getFiles({
    prefix: storagePath.path,
  });
  const fileNames: StoragePath[] = [];
  files.forEach((file) => {
    fileNames.push({
      bucket: storagePath.bucket,
      path: file.name,
    });
  });
  return fileNames;
}

/** Downloads a file from GCS and returns its local path. */
async function downloadFile(storagePath: StoragePath): Promise<string> {
  const storage = await connectToStorage();
  const destination = path.join(__dirname, storagePath.path);
  mkdir(path.dirname(destination), { recursive: true });
  await storage
    .bucket(storagePath.bucket)
    .file(storagePath.path)
    .download({ destination });
  return destination;
}

/** Returns whether the GCS file exists. */
async function fileExists(storagePath: StoragePath): Promise<boolean> {
  const storage = await connectToStorage();
  const files = await storage
    .bucket(storagePath.bucket)
    .getFiles({ prefix: storagePath.path });
  return files[0].length > 0;
}

/** Downloads a string file from GCS and parses its contents. */
export async function downloadJson(
  fileName: string,
  bucket: string
): Promise<{ [key: string]: any } | null> {
  const storagePath = getStoragePath(bucket);
  storagePath.path = path.join(storagePath.path, fileName);
  const exists = await fileExists(storagePath);
  if (!exists) {
    return null;
  }
  const localPath = await downloadFile(storagePath);
  const data = await fs.readFileSync(localPath, "utf8");
  return JSON.parse(data);
}

/** Downloads a CSV file from GCS and parses its contents. */
export async function downloadCsvFile<Type>(
  csvFileName: string,
  bucket: string
): Promise<Type[] | null> {
  const storagePath = getStoragePath(bucket);
  storagePath.path = path.join(storagePath.path, csvFileName);
  const exists = await fileExists(storagePath);
  if (!exists) {
    return null;
  }
  const localPath = await downloadFile(storagePath);
  try {
    return await new Promise<Type[]>((resolve, reject) => {
      const values: Type[] = [];
      fs.createReadStream(localPath)
        .pipe(
          parse({
            delimiter: ",",
            columns: true,
            ltrim: true,
          })
        )
        .on("data", (row: Type) => {
          values.push(row);
        })
        .on("end", () => {
          resolve(values);
        })
        .on("error", (e) => {
          reject(e);
        });
    });
  } catch (e) {
    console.error(e);
    return null;
  }
}

/** Uploads a string to a file in GCS and returns the remote path. */
async function uploadString(
  contents: string,
  fileName: string,
  bucket: string
): Promise<string> {
  const storagePath = getStoragePath(bucket);
  const remoteFileName = path.join(storagePath.path, fileName);
  const storage = await connectToStorage();
  await storage.bucket(storagePath.bucket).file(remoteFileName).save(contents);
  return path.join(storagePath.bucket, remoteFileName);
}

/** Uploads an array of objects to a CSV file in GCS and returns the remote path. */
export async function uploadCsvFile(
  data: Object[],
  fileName: string,
  bucket: string
): Promise<string> {
  const sortedOutputKeys: string[] = Object.keys(data[0]).sort();
  const csvOutput = Papa.unparse(data, {
    quotes: false,
    quoteChar: '"',
    escapeChar: '"',
    delimiter: ",",
    header: true,
    newline: "\r\n",
    skipEmptyLines: false,
    columns: sortedOutputKeys,
  });
  return await uploadString(csvOutput, fileName, bucket);
}
